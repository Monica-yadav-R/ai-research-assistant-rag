
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.model import Base, Document
from api.database import get_db
from api.main import app
import api.main as main


def run_test():
    # 1. Create an isolated SQLite database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    # 2. Create an isolated ChromaDB collection
    chroma_client = chromadb.EphemeralClient()
    collection = chroma_client.create_collection(
        name="document_delete_test"
    )

    main.get_chroma_collection = lambda: collection

    # 3. Create temporary PDF files
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        pdf_a = temp_path / "document_a.pdf"
        pdf_b = temp_path / "document_b.pdf"

        pdf_a.write_bytes(b"%PDF-1.4 test document A")
        pdf_b.write_bytes(b"%PDF-1.4 test document B")

        document_a_id = "a" * 64
        document_b_id = "b" * 64

        # 4. Insert test documents into SQLite
        with TestingSession() as db:
            db.add_all([
                Document(
                    id=document_a_id,
                    filename="document_a.pdf",
                    file_path=str(pdf_a),
                    status="processed",
                    total_pages=1,
                    total_chunks=1
                ),
                Document(
                    id=document_b_id,
                    filename="document_b.pdf",
                    file_path=str(pdf_b),
                    status="processed",
                    total_pages=1,
                    total_chunks=1
                )
            ])
            db.commit()

        # 5. Insert chunks into ChromaDB
        collection.add(
            ids=["docA_0", "docA_1", "docB_0", "docA_userB_0"],
            embeddings=[
                [0.1] * 384,
                [0.2] * 384,
                [0.3] * 384,
                [0.4] * 384
            ],
            documents=[
                "First chunk",
                "Second chunk",
                "Another document's chunk",
                "Same document ID, different user"
            ],
            metadatas=[
                {"document_id": "docA", "user_id": "userA"},
                {"document_id": "docA", "user_id": "userA"},
                {"document_id": "docB", "user_id": "userA"},
                {"document_id": "docA", "user_id": "userB"}
            ]
        )

        # 6. Override FastAPI database dependency
        def override_get_db():
            db = TestingSession()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 7. Call the actual deletion endpoint
            with TestClient(app) as client:
                response = client.delete(
                    f"/documents/{document_a_id}"
                )

            assert response.status_code == 200, response.text

            # 8. Verify SQLite
            with TestingSession() as db:
                deleted_a = db.execute(
                    select(Document).where(
                        Document.id == document_a_id
                    )
                ).scalar_one_or_none()

                remaining_b = db.execute(
                    select(Document).where(
                        Document.id == document_b_id
                    )
                ).scalar_one_or_none()

            assert deleted_a is None
            assert remaining_b is not None

            # 9. Verify ChromaDB
            remaining_chunks = collection.get()

            assert remaining_chunks["ids"] == ["b_chunk_0"]

            # 10. Verify PDF files
            assert not pdf_a.exists()
            assert pdf_b.exists()

            print("API response:", response.json())
            print("SQLite deletion: PASSED")
            print("ChromaDB deletion: PASSED")
            print("PDF deletion: PASSED")
            print("Unrelated document preservation: PASSED")
            print("Full document deletion integration test passed!")

        finally:
            app.dependency_overrides.pop(get_db, None)

    engine.dispose()


if __name__ == "__main__":
    run_test()


from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import select

from api.database import SessionLocal
from api.model import Document
from api.pgvector_store import (
    DocumentChunk,
    store_chunks,
    search_chunks
)
from embedding_generator import (
    load_embedding_model,
    generate_embeddings
)


TEST_USER_ID = "e1a27c83-d282-4a19-966f-41f0535dd83d"
TEST_DOCUMENT_ID = uuid4().hex

sample_chunks = [
    {
        "source": "pgvector_test.pdf",
        "page": 1,
        "text": "Rising temperatures can reduce crop productivity."
    },
    {
        "source": "pgvector_test.pdf",
        "page": 2,
        "text": "Deep learning uses neural networks to learn patterns."
    },
    {
        "source": "pgvector_test.pdf",
        "page": 3,
        "text": "Vector databases store numerical embeddings for similarity search."
    }
]

db = SessionLocal()

try:
    # 1. Create temporary parent document
    document = Document(
        id=TEST_DOCUMENT_ID,
        user_id=TEST_USER_ID,
        filename="pgvector_test.pdf",
        file_path="test-only",
        status="processed",
        total_pages=3,
        total_chunks=3,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(document)
    db.commit()

    # 2. Generate real embeddings
    model = load_embedding_model()

    embedded_chunks = generate_embeddings(
        sample_chunks,
        model
    )

    # 3. Store embeddings in Supabase
    stored_count = store_chunks(
        document_id=TEST_DOCUMENT_ID,
        user_id=TEST_USER_ID,
        embedded_chunks=embedded_chunks
    )

    print("Stored chunks:", stored_count)

    # 4. Generate question embedding
    question = "How does heat affect agricultural production?"

    question_vector = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # 5. Search Supabase using pgvector
    results = search_chunks(
        question_embedding=question_vector,
        user_id=TEST_USER_ID,
        top_k=3,
        document_id=TEST_DOCUMENT_ID
    )

    print("\nRetrieved results:")

    for result in results:
        print("\nText:", result["text"])
        print("Source:", result["source"])
        print("Page:", result["page"])
        print("Distance:", result["distance"])

    # 6. Verify retrieval
    assert stored_count == 3
    assert len(results) == 3
    assert "temperature" in results[0]["text"].lower()

    print("\npgvector semantic retrieval test passed!")

finally:
    # 7. Clean up temporary data
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == TEST_DOCUMENT_ID,
        DocumentChunk.user_id == TEST_USER_ID
    ).delete(synchronize_session=False)

    db.query(Document).filter(
        Document.id == TEST_DOCUMENT_ID,
        Document.user_id == TEST_USER_ID
    ).delete(synchronize_session=False)

    db.commit()
    db.close()

    print("Temporary test data cleaned up.")

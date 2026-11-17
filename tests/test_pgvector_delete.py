
from uuid import uuid4
from datetime import datetime, timezone

from api.database import SessionLocal
from api.model import Document
from api.pgvector_store import (
    DocumentChunk,
    store_chunks,
    delete_document_chunks
)

USER_A = "e1a27c83-d282-4a19-966f-41f0535dd83d"
USER_B = str(uuid4())

DOCUMENT_A = uuid4().hex
DOCUMENT_B = uuid4().hex

db = SessionLocal()

try:
    # Create a second temporary user for the isolation test
    from api.model import User

    user_b = User(
        id=USER_B,
        username=f"pgvector_test_{uuid4().hex[:8]}",
        email=f"pgvector_test_{uuid4().hex[:8]}@example.com",
        password_hash="test-only-not-a-real-password",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )

    db.add(user_b)

    # Create three temporary documents
    documents = [
        Document(
            id=DOCUMENT_A,
            user_id=USER_A,
            filename="user_a_document.pdf",
            file_path="test-only",
            status="processed",
            total_pages=1,
            total_chunks=1
        ),
        Document(
            id=DOCUMENT_B,
            user_id=USER_B,
            filename="user_b_document.pdf",
            file_path="test-only",
            status="processed",
            total_pages=1,
            total_chunks=1
        )
    ]

    db.add_all(documents)
    db.commit()

    # Store one chunk per user
    test_chunks = [
        {
            "text": "Temporary test chunk.",
            "source": "delete_test.pdf",
            "page": 1,
            "embedding": [0.1] * 384
        }
    ]

    store_chunks(DOCUMENT_A, USER_A, test_chunks)
    store_chunks(DOCUMENT_B, USER_B, test_chunks)

    # Delete User A's document chunks
    deleted = delete_document_chunks(DOCUMENT_A, USER_A)

    print("Deleted chunks:", deleted)

    # Verify remaining records
    remaining = db.query(DocumentChunk).filter(
        DocumentChunk.document_id.in_([DOCUMENT_A, DOCUMENT_B])
    ).all()

    assert deleted == 1
    assert len(remaining) == 1
    assert remaining[0].document_id == DOCUMENT_B
    assert remaining[0].user_id == USER_B

    print("User isolation verified.")
    print("pgvector deletion test passed!")

finally:
    # Clean up all temporary records
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id.in_([DOCUMENT_A, DOCUMENT_B])
    ).delete(synchronize_session=False)

    db.query(Document).filter(
        Document.id.in_([DOCUMENT_A, DOCUMENT_B])
    ).delete(synchronize_session=False)

    db.query(User).filter(User.id == USER_B).delete(
        synchronize_session=False
    )

    db.commit()
    db.close()

    print("Temporary test data cleaned up.")

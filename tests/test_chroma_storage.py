
import numpy as np
from uuid import uuid4

from api.chroma_store import get_chroma_collection,store_chunks



def main():

    collection = get_chroma_collection()

    # Unique ID so this test does not affect real documents.
    test_document_id = f"test-{uuid4()}"
    test_user_id = f"test-user-{uuid4()}"
    sample_chunks = [
        {
            "source": "sample_research.pdf",
            "page": 1,
            "text": "Machine learning identifies patterns in data.",
            "embedding": np.random.rand(384).astype(np.float32)
        },
        {
            "source": "sample_research.pdf",
            "page": 2,
            "text": "Deep learning uses neural networks.",
            "embedding": np.random.rand(384).astype(np.float32)
        },
        {
            "source": "sample_research.pdf",
            "page": 3,
            "text": "Vector databases support semantic search.",
            "embedding": np.random.rand(384).astype(np.float32)
        }
    ]

    try:
        # Store sample chunks.
        stored_count = store_chunks(
            collection=collection,
            document_id=test_document_id,
            user_id=test_user_id,
            embedded_chunks=sample_chunks
        )

        print("Stored chunks:", stored_count)

        # Retrieve the records belonging to this test.
        records = collection.get(
            where={"document_id": test_document_id},
            include=["documents", "metadatas", "embeddings"]
        )

        print("Retrieved chunks:", len(records["ids"]))

        # Verify storage.
        assert stored_count == 3
        assert len(records["ids"]) == 3
        assert len(records["documents"]) == 3
        assert len(records["metadatas"]) == 3

        embeddings = np.asarray(records["embeddings"])
        assert embeddings.shape == (3, 384)

        for metadata in records["metadatas"]:
            assert metadata["document_id"] == test_document_id

        print("Embedding shape:", embeddings.shape)
        print("Metadata:", records["metadatas"])
        print("Storage verification successful.")

    finally:
        # Remove temporary test records.
        collection.delete(
            where={"document_id": test_document_id}
        )
        print("Temporary test records cleaned up.")


if __name__ == "__main__":
    main()

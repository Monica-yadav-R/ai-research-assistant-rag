from uuid import uuid4
import inspect

from api.chroma_store import (
    get_chroma_collection,
    store_chunks,
    search_chunks
)

from embedding_generator import (
    load_embedding_model,
    generate_embeddings
)

def main():

    collection = get_chroma_collection()

    test_document_id = f"retrieval-test-{uuid4()}"
    test_user_id = f"retrieval-user-{uuid4()}"

    sample_chunks = [
        {
            "source": "sample_research.pdf",
            "page": 1,
            "text": "Rising temperatures can reduce crop productivity."
        },
        {
            "source": "sample_research.pdf",
            "page": 2,
            "text": "Deep learning uses neural networks to learn patterns."
        },
        {
            "source": "sample_research.pdf",
            "page": 3,
            "text": "Vector databases store numerical embeddings for similarity search."
        }
    ]

    try:
        model = load_embedding_model()

        embedded_chunks = generate_embeddings(
            sample_chunks,
            model
        )

        stored_count = store_chunks(
            collection=collection,
            document_id=test_document_id,
            user_id=test_user_id,
            embedded_chunks=embedded_chunks
        )

        print("Stored chunks:", stored_count)

        question = "How does heat affect agricultural production?"

        question_vector = model.encode(
            question,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        results = search_chunks(
            collection=collection,
            question_embedding=question_vector,
            user_id=test_user_id,
            top_k=3,
            document_id=test_document_id
        )

        print("\nRetrieved results:")
    
        for result in results:
            print("\nText:", result["text"])
            print("Source:", result["source"])
            print("Page:", result["page"])
            print("Distance:", result["distance"])

        assert len(results) == 3

        assert "temperature" in results[0]["text"].lower()

        print("\nSemantic retrieval test successful.")

    finally:
        collection.delete(
            where={"document_id": test_document_id}
        )

        print("Temporary records cleaned up.")


if __name__ == "__main__":
    main()
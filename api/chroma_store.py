from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

#Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent ChromaDB storage directory
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

def get_chroma_collection():
    """
    Initialize a persistent chromaDB client
    and return the research documents collection.
    """
    import chromadb

    CHROMA_DIR.mkdir(parents=True,exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name="research_documents",
        metadata={"hnsw:space":"cosine"}
    )

    return collection


def store_chunks(
    collection,
    document_id: str,
    user_id: str,
    embedded_chunks: list[dict]
) -> int:
    """
    Store embedded PDF chunks in ChromaDB with user ownership.
    """

    if not document_id or not document_id.strip():
        raise ValueError("Document ID cannot be empty.")

    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty.")

    if not embedded_chunks:
        raise ValueError("No embedded chunks to store.")

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(embedded_chunks):

        if not isinstance(chunk, dict):
            raise TypeError("Each chunk must be a dictionary.")

        embedding = np.asarray(
            chunk["embedding"],
            dtype=np.float32
        )

        if embedding.ndim != 1 or embedding.size == 0:
            raise ValueError("Invalid embedding dimensions.")

        if not np.isfinite(embedding).all():
            raise ValueError("Embedding contains invalid values.")

        if not isinstance(chunk["text"], str) or not chunk["text"].strip():
            raise ValueError("Chunk text cannot be empty.")

        if not isinstance(chunk["source"], str) or not chunk["source"].strip():
            raise ValueError("Chunk source cannot be empty.")

        if (
            isinstance(chunk["page"], bool)
            or not isinstance(chunk["page"], int)
            or chunk["page"] <= 0
        ):
            raise ValueError("Page must be a positive integer.")

        ids.append(f"{document_id}_{index}")
        embeddings.append(embedding.tolist())
        documents.append(chunk["text"])

        metadatas.append({
            "document_id": document_id,
            "user_id": user_id,
            "source": chunk["source"],
            "page": chunk["page"],
            "chunk_index": index
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)

def search_chunks(
    collection: Collection,
    question_embedding: list[float] | np.ndarray,
    user_id: str,
    top_k: int = 3,
    document_id: str | None = None
):
    # Validate user ID
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string.")

    # Convert the question embedding into a NumPy array
    question_embedding = np.asarray(
        question_embedding,
        dtype=np.float32
    )

    if question_embedding.ndim != 1:
        raise ValueError("Question embedding must be a one-dimensional vector.")

    if question_embedding.shape[0] != 384:
        raise ValueError("Question embedding must contain 384 dimensions.")

    if not np.isfinite(question_embedding).all():
        raise ValueError("Question embedding contains invalid values.")

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    if document_id is not None:
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("document_id must be a non-empty string.")

    # Always restrict retrieval to the authenticated user
    where_filter = {"user_id": user_id}

    # Optionally restrict retrieval to one document
    if document_id is not None:
        where_filter = {
            "$and": [
                {"user_id": user_id},
                {"document_id": document_id}
            ]
        }

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    for text, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        retrieved_chunks.append({
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": float(distance)
        })

    return retrieved_chunks

def document_exists(collection, document_id: str) -> bool:
    results = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
        limit=1,
    )

    return len(results["ids"]) > 0



def delete_document_chunks(
    collection: Collection,
    document_id: str,
    user_id: str
) -> int:
    """
    Delete ChromaDB chunks belonging to a specific user's document.

    Returns the number of deleted chunks.
    """
    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("Document ID cannot be empty.")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("User ID cannot be empty.")

    results = collection.get(
        where={
            "$and": [
                {"document_id": document_id},
                {"user_id": user_id}
            ]
        },
        include=["metadatas"]
    )

    chunk_ids = results["ids"]

    if not chunk_ids:
        return 0

    collection.delete(ids=chunk_ids)

    return len(chunk_ids)
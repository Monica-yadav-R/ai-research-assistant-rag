
import numpy as np


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model(
    device: str | None = None,
):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        MODEL_NAME,
        device=device,
    )


def generate_embeddings(
    chunks: list[dict],
    model,
) -> list[dict]:
    if not chunks:
        return []

    texts = []

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise TypeError(f"Chunk at index {index} must be a dictionary")

        if "text" not in chunk:
            raise ValueError(f"Chunk at index {index} is missing 'text'")

        text = chunk["text"]

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"Chunk at index {index} must contain non-empty text"
            )

        texts.append(text)

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embedded_chunks = []

    for chunk, vector in zip(chunks, vectors):
        embedded_chunks.append({
            **chunk,
            "embedding": vector,
        })

    return embedded_chunks

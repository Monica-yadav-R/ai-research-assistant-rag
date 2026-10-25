
def chunk_pages(
    pages: list[dict],
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step_size = chunk_size - overlap

    for page in pages:
        words = page["text"].split()

        if not words:
            continue

        for start in range(0, len(words), step_size):
            chunk_words = words[start:start + chunk_size]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "source": page["source"],
                "page": page["page"],
                "text": chunk_text,
            })

            if start + chunk_size >= len(words):
                break

    return chunks

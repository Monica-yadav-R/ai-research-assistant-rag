import pymupdf
from pathlib import Path

def extract_pdf_pages(path: str) -> list[dict]:
    pdf_path = Path(path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, received: {pdf_path.name}")

    metadata = []
    source = pdf_path.name
    with pymupdf.open(path) as doc:
        for page_number, page in enumerate(doc,start=1):
            data = {
                "source":source,
                "page": page_number,
                "text": page.get_text()
            }
            metadata.append(data)
    return metadata


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 400,
    overlap: int = 80,
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

def pdf_to_chunks(
        path:str,
        chunk_size:int=300,
        overlap:int=50
    ):
    pages = extract_pdf_pages(path)
    if not any(page["text"].strip() for page in pages):
        raise ValueError("No extractable text was found in the PDF.")
    chunks = chunk_pages(
        pages,
        chunk_size=chunk_size,
        overlap=overlap)
    if not chunks:
        raise ValueError("There is no texts")
    return chunks

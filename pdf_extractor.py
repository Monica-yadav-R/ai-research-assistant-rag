import pymupdf
from pathlib import Path

def extract_pdf_pages(path: str) -> list[dict]:
    pdf_path = Path(path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file,received: {pdf_path.name}")

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

import pytest
import pymupdf

from pdf_extractor import (
    chunk_pages,
    pdf_to_chunks,
    extract_pdf_pages
)


# --------------------------------------------------
# 1. UNIT TESTS: CHUNK CREATION
# --------------------------------------------------

def create_page(text, page=1, source="paper.pdf"):
    return {
        "source": source,
        "page": page,
        "text": text
    }


def test_normal_chunk_creation():
    words = [f"word{i}" for i in range(700)]

    pages = [create_page(" ".join(words))]

    chunks = chunk_pages(
        pages,
        chunk_size=300,
        overlap=50
    )

    assert len(chunks) > 0


def test_custom_chunk_size():
    words = [f"word{i}" for i in range(500)]

    pages = [create_page(" ".join(words))]

    chunks = chunk_pages(
        pages,
        chunk_size=200,
        overlap=30
    )

    for chunk in chunks:
        assert len(chunk["text"].split()) <= 200


def test_custom_overlap():
    words = [f"word{i}" for i in range(500)]

    pages = [create_page(" ".join(words))]

    chunks = chunk_pages(
        pages,
        chunk_size=200,
        overlap=50
    )

    assert len(chunks) >= 2

    first_words = chunks[0]["text"].split()
    second_words = chunks[1]["text"].split()

    assert first_words[-50:] == second_words[:50]


def test_default_parameters():
    words = [f"word{i}" for i in range(400)]

    pages = [create_page(" ".join(words))]

    chunks = chunk_pages(pages)

    assert len(chunks) == 2

    first_words = chunks[0]["text"].split()
    second_words = chunks[1]["text"].split()

    assert len(first_words) == 300
    assert len(second_words) == 150
    assert first_words[-50:] == second_words[:50]


# --------------------------------------------------
# 2. EDGE CASE TESTS
# --------------------------------------------------

def test_empty_page():
    pages = [create_page("")]

    chunks = chunk_pages(pages)

    assert chunks == []


def test_multiple_pages():
    pages = [
        create_page(" ".join(["apple"] * 400), page=1),
        create_page(" ".join(["banana"] * 400), page=2)
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=200,
        overlap=50
    )

    assert all(
        chunk["page"] in [1, 2]
        for chunk in chunks
    )

    assert any(chunk["page"] == 1 for chunk in chunks)
    assert any(chunk["page"] == 2 for chunk in chunks)


def test_source_metadata():
    pages = [
        create_page(
            " ".join(["research"] * 100),
            source="attention.pdf"
        )
    ]

    chunks = chunk_pages(pages)

    assert chunks[0]["source"] == "attention.pdf"


def test_page_metadata():
    pages = [
        create_page(
            " ".join(["research"] * 100),
            page=5
        )
    ]

    chunks = chunk_pages(pages)

    assert chunks[0]["page"] == 5


def test_short_text():
    pages = [create_page("one two three four five")]

    chunks = chunk_pages(
        pages,
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) == 1
    assert len(chunks[0]["text"].split()) == 5


def test_exact_chunk_size():
    pages = [
        create_page(" ".join(["word"] * 300))
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=300,
        overlap=50
    )

    assert len(chunks) == 1
    assert len(chunks[0]["text"].split()) == 300


def test_text_slightly_larger_than_chunk_size():
    pages = [
        create_page(" ".join(["word"] * 301))
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=300,
        overlap=50
    )

    assert len(chunks) == 2
    assert len(chunks[0]["text"].split()) == 300
    assert len(chunks[1]["text"].split()) == 51


# --------------------------------------------------
# 3. INPUT VALIDATION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "chunk_size",
    [0, -1, -100]
)
def test_invalid_chunk_size(chunk_size):

    pages = [create_page("some research text")]

    with pytest.raises(ValueError):
        chunk_pages(
            pages,
            chunk_size=chunk_size,
            overlap=10
        )


def test_negative_overlap():

    pages = [create_page("some research text")]

    with pytest.raises(ValueError):
        chunk_pages(
            pages,
            chunk_size=100,
            overlap=-1
        )


def test_overlap_equal_to_chunk_size():

    pages = [create_page("some research text")]

    with pytest.raises(ValueError):
        chunk_pages(
            pages,
            chunk_size=100,
            overlap=100
        )


def test_overlap_greater_than_chunk_size():

    pages = [create_page("some research text")]

    with pytest.raises(ValueError):
        chunk_pages(
            pages,
            chunk_size=100,
            overlap=150
        )


# --------------------------------------------------
# 4. PDF EXTRACTION AND INTEGRATION TESTS
# --------------------------------------------------

def test_empty_pdf_text(monkeypatch, tmp_path):

    monkeypatch.setattr(
        "pdf_extractor.extract_pdf_pages",
        lambda path: [
            create_page("")
        ]
    )

    pdf_path = tmp_path / "empty.pdf"
    pdf_path.touch()

    with pytest.raises(ValueError):
        pdf_to_chunks(pdf_path)


def test_missing_pdf():

    with pytest.raises(FileNotFoundError):
        extract_pdf_pages("missing_file.pdf")


def test_invalid_pdf_extension(tmp_path):

    invalid_file = tmp_path / "paper.txt"
    invalid_file.write_text("This is not a PDF")

    with pytest.raises(ValueError):
        extract_pdf_pages(invalid_file)


def test_actual_pdf_chunking(tmp_path):

    pdf_path = tmp_path / "sample.pdf"

    doc = pymupdf.open()

    page = doc.new_page()

    page.insert_text(
        (50, 50),
        " ".join(["research"] * 500)
    )

    doc.save(pdf_path)
    doc.close()

    chunks = pdf_to_chunks(
        pdf_path,
        chunk_size=200,
        overlap=30
    )

    assert len(chunks) > 0

    assert all(
        chunk["source"] == "sample.pdf"
        for chunk in chunks
    )

    assert all(
        chunk["page"] == 1
        for chunk in chunks
    )

    assert all(
        len(chunk["text"].split()) <= 200
        for chunk in chunks
    )

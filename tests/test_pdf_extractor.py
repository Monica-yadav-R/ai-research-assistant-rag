
import tempfile
import unittest
from pathlib import Path

import pymupdf

from pdf_extractor import extract_pdf_pages


class TestExtractPdfPages(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pdf_path = Path(self.temp_dir.name) / "sample.pdf"

        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((72, 72), "First page research text")

            doc.new_page()  # Intentionally blank page

            page = doc.new_page()
            page.insert_text((72, 72), "Third page findings")

            doc.save(self.pdf_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extracts_text_and_page_metadata(self):
        records = extract_pdf_pages(str(self.pdf_path))

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["source"], "sample.pdf")
        self.assertEqual(records[0]["page"], 1)
        self.assertIn("First page research text", records[0]["text"])

    def test_preserves_blank_page(self):
        records = extract_pdf_pages(str(self.pdf_path))

        self.assertEqual(records[1]["page"], 2)
        self.assertEqual(records[1]["text"], "")

    def test_missing_file_raises_error(self):
        missing_path = Path(self.temp_dir.name) / "missing.pdf"

        with self.assertRaises(FileNotFoundError):
            extract_pdf_pages(str(missing_path))

    def test_rejects_wrong_extension(self):
        text_path = Path(self.temp_dir.name) / "sample.txt"
        text_path.write_text("Not a PDF", encoding="utf-8")

        with self.assertRaises(ValueError):
            extract_pdf_pages(str(text_path))

    def test_corrupt_pdf_raises_error(self):
        corrupt_path = Path(self.temp_dir.name) / "corrupt.pdf"
        corrupt_path.write_text("This is not a real PDF", encoding="utf-8")

        with self.assertRaises(pymupdf.FileDataError):
            extract_pdf_pages(str(corrupt_path))

if __name__ == "__main__":
    unittest.main()

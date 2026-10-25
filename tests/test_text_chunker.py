import unittest

from text_chunker import chunk_pages


class TestChunkPages(unittest.TestCase):

    def test_creates_one_chunk_for_short_text(self):
        pages = [
            {
                "source": "sample.pdf",
                "page": 1,
                "text": "The model learns",
            }
        ]

        chunks = chunk_pages(pages, chunk_size=5, overlap=1)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["text"], "The model learns")
        self.assertEqual(chunks[0]["source"], "sample.pdf")
        self.assertEqual(chunks[0]["page"], 1)

    def test_creates_multiple_chunks_with_overlap(self):
        pages = [
            {
                "source": "sample.pdf",
                "page": 2,
                "text": "The model learns from data and predicts outcomes",
            }
        ]

        chunks = chunk_pages(pages, chunk_size=4, overlap=1)

        self.assertEqual(
            [chunk["text"] for chunk in chunks],
            [
                "The model learns from",
                "from data and predicts",
                "predicts outcomes",
            ],
        )

    def test_skips_blank_page(self):
        pages = [
            {
                "source": "sample.pdf",
                "page": 3,
                "text": "   \n  ",
            }
        ]

        chunks = chunk_pages(pages)

        self.assertEqual(chunks, [])

    def test_rejects_zero_chunk_size(self):
        with self.assertRaises(ValueError):
            chunk_pages([], chunk_size=0)

    def test_rejects_negative_overlap(self):
        with self.assertRaises(ValueError):
            chunk_pages([], chunk_size=5, overlap=-1)

    def test_rejects_overlap_equal_to_chunk_size(self):
        with self.assertRaises(ValueError):
            chunk_pages([], chunk_size=5, overlap=5)
    
    def test_does_not_create_redundant_final_chunk(self):
        pages = [
            {
                "source": "sample.pdf",
                "page": 1,
                "text": "The model learns from data",
            }
        ]

        chunks = chunk_pages(pages, chunk_size=4, overlap=3)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(
            [chunk["text"] for chunk in chunks],
            [
                "The model learns from",
                "model learns from data",
            ],
        )
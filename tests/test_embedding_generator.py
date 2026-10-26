
import unittest
import numpy as np
from unittest.mock import patch
from embedding_generator import generate_embeddings, load_embedding_model

class FakeModel:
    def encode(
        self,
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ):
        return np.array([
            [1.0, 0.0, 0.0]
            for _ in texts
        ])


class TestGenerateEmbeddings(unittest.TestCase):

    def setUp(self):
        self.model = FakeModel()
        self.chunks = [
            {
                "source": "paper.pdf",
                "page": 1,
                "text": "Neural networks learn patterns.",
            },
            {
                "source": "paper.pdf",
                "page": 2,
                "text": "Models learn from examples.",
            },
        ]

    def test_adds_embeddings_and_preserves_metadata(self):
        result = generate_embeddings(self.chunks, self.model)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["source"], "paper.pdf")
        self.assertEqual(result[0]["page"], 1)
        self.assertEqual(
            result[0]["text"],
            "Neural networks learn patterns.",
        )
        np.testing.assert_array_equal(
            result[0]["embedding"],
            np.array([1.0, 0.0, 0.0]),
        )

    def test_does_not_modify_original_chunks(self):
        original_text = self.chunks[0]["text"]

        generate_embeddings(self.chunks, self.model)

        self.assertNotIn("embedding", self.chunks[0])
        self.assertEqual(self.chunks[0]["text"], original_text)

    def test_empty_input_returns_empty_list(self):
        result = generate_embeddings([], self.model)

        self.assertEqual(result, [])

    def test_missing_text_raises_error(self):
        with self.assertRaisesRegex(ValueError, "missing 'text'"):
            generate_embeddings(
                [{"source": "paper.pdf", "page": 1}],
                self.model,
            )

    def test_empty_text_raises_error(self):
        with self.assertRaisesRegex(ValueError, "non-empty text"):
            generate_embeddings(
                [{"text": "   "}],
                self.model,
            )

    def test_non_dictionary_chunk_raises_error(self):
        with self.assertRaisesRegex(TypeError, "must be a dictionary"):
            generate_embeddings(["not a chunk"], self.model)

    @patch("embedding_generator.SentenceTransformer")
    def test_load_embedding_model_uses_requested_device(self, mock_transformer):
        model = load_embedding_model(device="cuda")

        mock_transformer.assert_called_once_with(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cuda",
        )
        self.assertIs(model, mock_transformer.return_value)



if __name__ == "__main__":
    unittest.main()

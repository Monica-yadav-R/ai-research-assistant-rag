
import unittest
from unittest.mock import Mock
import numpy as np

from retrieval_experiment import question_embedding


class TestQuestionEmbedding(unittest.TestCase):

    def setUp(self):
        """Create a mock embedding model for each test."""
        self.model = Mock()
        self.expected_embedding = np.array([0.6, 0.8], dtype=np.float32)
        self.model.encode.return_value = self.expected_embedding

    def test_valid_question_returns_embedding(self):
        """A valid question should return the model's embedding."""
        result = question_embedding("What is attention?", self.model)

        np.testing.assert_array_equal(result, self.expected_embedding)

    def test_model_receives_correct_arguments(self):
        """The model should receive the expected encoding options."""
        question_embedding("What is attention?", self.model)

        self.model.encode.assert_called_once_with(
            "What is attention?",
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    def test_none_model_raises_value_error(self):
        """A missing embedding model should raise ValueError."""
        with self.assertRaisesRegex(ValueError, "Embedding model cannot be None"):
            question_embedding("What is attention?", None)

    def test_model_is_not_called_when_none(self):
        """No encoding should happen if the model is None."""
        # The function should reject None before calling encode().
        with self.assertRaises(ValueError):
            question_embedding("What is attention?", None)

    def test_empty_question(self):
        """An empty question should raise ValueError."""
        with self.assertRaisesRegex(ValueError, "Question cannot be empty"):
            question_embedding("", self.model)

        self.model.encode.assert_not_called()


    def test_whitespace_question(self):
        """A whitespace-only question should raise ValueError."""
        with self.assertRaisesRegex(ValueError, "Question cannot be empty"):
            question_embedding("   ", self.model)

        self.model.encode.assert_not_called()

    def test_embedding_is_numpy_array(self):
        """The configured model returns a NumPy array."""
        result = question_embedding("What is attention?", self.model)

        self.assertIsInstance(result, np.ndarray)

    def test_non_string_question_raises_type_error(self):
        """A non-string question should raise TypeError."""
        with self.assertRaisesRegex(TypeError, "Question should be a string"):
            question_embedding(123, self.model)

        self.model.encode.assert_not_called()


    def test_none_question_raises_type_error(self):
        """A None question should raise TypeError."""
        with self.assertRaisesRegex(TypeError, "Question should be a string"):
            question_embedding(None, self.model)

        self.model.encode.assert_not_called()
        
if __name__ == "__main__":
    unittest.main()

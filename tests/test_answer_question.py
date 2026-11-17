import unittest
from unittest.mock import patch

import numpy as np

from retrieval_experiment import (
    answer_question,
    INSUFFICIENT_EVIDENCE,
)


class TestAnswerQuestion(unittest.TestCase):

    def setUp(self):
        self.question = "What architecture does the paper propose?"
        self.model = object()
        self.index = object()
        self.stored_chunks = [
            {
                "source": "paper.pdf",
                "page": 3,
                "text": "The paper proposes an encoder-decoder architecture.",
            }
        ]

        self.query_vector = np.array([0.1, 0.2, 0.3])

        self.relevant_result = {
            "source": "paper.pdf",
            "page": 3,
            "text": "The paper proposes an encoder-decoder architecture.",
            "score": 0.75,
        }

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_valid_relevant_results_call_llm(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector
        mock_search_chunks.return_value = [self.relevant_result]
        mock_llm_generation.return_value = "The paper uses an encoder-decoder architecture."

        answer = answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
            min_similarity=0.30,
        )

        self.assertEqual(
            answer,
            "The paper uses an encoder-decoder architecture.",
        )

        mock_llm_generation.assert_called_once_with(
            self.question,
            [self.relevant_result],
        )

    @patch("retrieval_experiment.question_embedding")
    def test_empty_question_raises_value_error(
        self,
        mock_question_embedding,
    ):
        with self.assertRaises(ValueError):
            answer_question(
                "",
                self.model,
                self.index,
                self.stored_chunks,
            )

        mock_question_embedding.assert_not_called()

    @patch("retrieval_experiment.question_embedding")
    def test_non_string_question_raises_type_error(
        self,
        mock_question_embedding,
    ):
        with self.assertRaises(TypeError):
            answer_question(
                None,
                self.model,
                self.index,
                self.stored_chunks,
            )

        mock_question_embedding.assert_not_called()

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_empty_results_return_insufficient_evidence(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector
        mock_search_chunks.return_value = []

        answer = answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
        )

        self.assertEqual(answer, INSUFFICIENT_EVIDENCE)
        mock_llm_generation.assert_not_called()

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_all_scores_below_threshold_do_not_call_llm(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": 0.20,
            },
            {
                **self.relevant_result,
                "score": 0.25,
            },
        ]

        answer = answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
            min_similarity=0.30,
        )

        self.assertEqual(answer, INSUFFICIENT_EVIDENCE)
        mock_llm_generation.assert_not_called()

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_only_relevant_results_are_sent_to_llm(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector

        relevant = {
            **self.relevant_result,
            "score": 0.75,
        }

        irrelevant = {
            **self.relevant_result,
            "score": 0.10,
        }

        mock_search_chunks.return_value = [
            relevant,
            irrelevant,
        ]

        mock_llm_generation.return_value = "Expected answer."

        answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
            min_similarity=0.30,
        )

        mock_llm_generation.assert_called_once_with(
            self.question,
            [relevant],
        )

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_score_equal_to_threshold_is_accepted(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector

        result = {
            **self.relevant_result,
            "score": 0.30,
        }

        mock_search_chunks.return_value = [result]
        mock_llm_generation.return_value = "Expected answer."

        answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
            min_similarity=0.30,
        )

        mock_llm_generation.assert_called_once_with(
            self.question,
            [result],
        )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_missing_score_raises_value_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        result = {
            "source": "paper.pdf",
            "page": 3,
            "text": "Some evidence.",
        }

        mock_search_chunks.return_value = [result]

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_string_score_raises_type_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": "0.75",
            }
        ]

        with self.assertRaises(TypeError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_boolean_score_raises_type_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": True,
            }
        ]

        with self.assertRaises(TypeError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_nan_score_raises_value_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": np.nan,
            }
        ]

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_infinite_score_raises_value_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": np.inf,
            }
        ]

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    def test_invalid_threshold_type_raises_type_error(self):

        with self.assertRaises(TypeError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity="0.30",
            )

    def test_boolean_threshold_raises_type_error(self):

        with self.assertRaises(TypeError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity=True,
            )

    def test_threshold_outside_range_raises_value_error(self):

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity=1.5,
            )

    def test_infinite_threshold_raises_value_error(self):

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity=np.inf,
            )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_negative_infinite_score_raises_value_error(
        self,
        mock_search_chunks,
        mock_question_embedding,
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.return_value = [
            {
                **self.relevant_result,
                "score": -np.inf,
            }
        ]

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

    def test_nan_threshold_raises_value_error(self):

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity=np.nan,
            )

    def test_threshold_below_negative_one_raises_value_error(self):

        with self.assertRaises(ValueError):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
                min_similarity=-1.5,
            )

    @patch("retrieval_experiment.llm_generation")
    @patch("retrieval_experiment.search_chunks")
    @patch("retrieval_experiment.question_embedding")
    def test_search_chunks_receives_expected_arguments(
        self,
        mock_question_embedding,
        mock_search_chunks,
        mock_llm_generation,
    ):
        mock_question_embedding.return_value = self.query_vector
        mock_search_chunks.return_value = [self.relevant_result]
        mock_llm_generation.return_value = "Expected answer."

        answer_question(
            self.question,
            self.model,
            self.index,
            self.stored_chunks,
            min_similarity=0.30,
        )

        mock_question_embedding.assert_called_once_with(
            self.question,
            self.model,
        )

        mock_search_chunks.assert_called_once_with(
            self.index,
            self.stored_chunks,
            self.query_vector,
            top_k=3,
        )

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_embedding_failure_propagates(
        self, mock_search_chunks, mock_question_embedding
    ):
        mock_question_embedding.side_effect = RuntimeError(
            "Embedding model unavailable"
        )

        with self.assertRaisesRegex(
            RuntimeError, "Embedding model unavailable"
        ):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )

        mock_search_chunks.assert_not_called()

    @patch("retrieval_experiment.question_embedding")
    @patch("retrieval_experiment.search_chunks")
    def test_retrieval_failure_propagates(
        self, mock_search_chunks, mock_question_embedding
    ):
        mock_question_embedding.return_value = self.query_vector

        mock_search_chunks.side_effect = RuntimeError(
            "FAISS retrieval failed"
        )

        with self.assertRaisesRegex(
            RuntimeError, "FAISS retrieval failed"
        ):
            answer_question(
                self.question,
                self.model,
                self.index,
                self.stored_chunks,
            )  

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch
import httpx
import ollama

from retrieval_experiment import llm_generation


VALID_QUESTION = "What is attention?"

VALID_RESULT = {
    "source": "attention_paper.pdf",
    "page": 1,
    "text": "Attention computes relationships between tokens."
}


class TestLLMGeneration(unittest.TestCase):

    # 1. Empty results
    @patch("retrieval_experiment.ollama.generate")
    def test_empty_results_returns_insufficient_evidence(self, mock_generate):
        result = llm_generation(VALID_QUESTION, [])

        self.assertIn("not provide enough information", result)
        mock_generate.assert_not_called()

    # 2. Question validation
    def test_non_string_question_raises_type_error(self):
        with self.assertRaises(TypeError):
            llm_generation(123, [])

    def test_empty_question_raises_value_error(self):
        with self.assertRaises(ValueError):
            llm_generation("", [])

    def test_whitespace_question_raises_value_error(self):
        with self.assertRaises(ValueError):
            llm_generation("   ", [])

    # 3. Results validation
    def test_non_list_results_raises_type_error(self):
        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, "not a list")

    def test_non_dictionary_chunk_raises_type_error(self):
        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, ["not a dictionary"])

    # 4. Source validation
    def test_missing_source_raises_value_error(self):
        result = {**VALID_RESULT}
        del result["source"]

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_non_string_source_raises_type_error(self):
        result = {**VALID_RESULT, "source": 123}

        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, [result])

    def test_empty_source_raises_value_error(self):
        result = {**VALID_RESULT, "source": ""}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_whitespace_source_raises_value_error(self):
        result = {**VALID_RESULT, "source": "   "}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    # 5. Page validation
    def test_missing_page_raises_value_error(self):
        result = {**VALID_RESULT}
        del result["page"]

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_non_integer_page_raises_type_error(self):
        result = {**VALID_RESULT, "page": "1"}

        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, [result])

    def test_boolean_page_raises_type_error(self):
        result = {**VALID_RESULT, "page": True}

        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, [result])

    def test_zero_page_raises_value_error(self):
        result = {**VALID_RESULT, "page": 0}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_negative_page_raises_value_error(self):
        result = {**VALID_RESULT, "page": -1}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    # 6. Text validation
    def test_missing_text_raises_value_error(self):
        result = {**VALID_RESULT}
        del result["text"]

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_non_string_text_raises_type_error(self):
        result = {**VALID_RESULT, "text": 123}

        with self.assertRaises(TypeError):
            llm_generation(VALID_QUESTION, [result])

    def test_empty_text_raises_value_error(self):
        result = {**VALID_RESULT, "text": ""}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    def test_whitespace_text_raises_value_error(self):
        result = {**VALID_RESULT, "text": "   "}

        with self.assertRaises(ValueError):
            llm_generation(VALID_QUESTION, [result])

    # 7. Successful generation
    @patch("retrieval_experiment.ollama.generate")
    def test_valid_evidence_returns_llm_answer(self, mock_generate):
        mock_generate.return_value = {
            "response": "Attention computes relationships between tokens."
        }

        result = llm_generation(VALID_QUESTION, [VALID_RESULT])

        self.assertEqual(
            result,
            "Attention computes relationships between tokens."
        )
        mock_generate.assert_called_once()

    # 8. Ollama service failures
    @patch("retrieval_experiment.ollama.generate")
    def test_ollama_response_error_is_wrapped(self, mock_generate):
        mock_generate.side_effect = ollama.ResponseError("Model error")

        with self.assertRaises(RuntimeError) as context:
            llm_generation(VALID_QUESTION, [VALID_RESULT])

        self.assertIsInstance(context.exception.__cause__, ollama.ResponseError)

    @patch("retrieval_experiment.ollama.generate")
    def test_connection_error_is_wrapped(self, mock_generate):
        mock_generate.side_effect = httpx.ConnectError("Connection failed")

        with self.assertRaises(RuntimeError) as context:
            llm_generation(VALID_QUESTION, [VALID_RESULT])

        self.assertIsInstance(context.exception.__cause__, httpx.ConnectError)

    @patch("retrieval_experiment.ollama.generate")
    def test_timeout_error_is_wrapped(self, mock_generate):
        mock_generate.side_effect = httpx.TimeoutException("Request timed out")

        with self.assertRaises(RuntimeError) as context:
            llm_generation(VALID_QUESTION, [VALID_RESULT])

        self.assertIsInstance(context.exception.__cause__, httpx.TimeoutException)

    # 9. LLM response validation
    @patch("retrieval_experiment.ollama.generate")
    def test_missing_response_field_raises_runtime_error(self, mock_generate):
        mock_generate.return_value = {}

        with self.assertRaises(RuntimeError):
            llm_generation(VALID_QUESTION, [VALID_RESULT])

    @patch("retrieval_experiment.ollama.generate")
    def test_empty_llm_response_raises_runtime_error(self, mock_generate):
        mock_generate.return_value = {"response": ""}

        with self.assertRaises(RuntimeError):
            llm_generation(VALID_QUESTION, [VALID_RESULT])

    @patch("retrieval_experiment.ollama.generate")
    def test_non_string_llm_response_raises_runtime_error(self, mock_generate):
        mock_generate.return_value = {"response": 123}

        with self.assertRaises(RuntimeError):
            llm_generation(VALID_QUESTION, [VALID_RESULT])


if __name__ == "__main__":
    unittest.main()

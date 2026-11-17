
import unittest

import faiss
import numpy as np

from vector_store import build_faiss_index, search_chunks


class TestBuildFaissIndex(unittest.TestCase):

    def setUp(self):
        self.chunks = [
            {
                "source": "paper1.pdf",
                "page": 1,
                "text": "Machine learning research",
                "embedding": np.array([1.0, 0.0, 0.0])
            },
            {
                "source": "paper2.pdf",
                "page": 2,
                "text": "Deep learning research",
                "embedding": np.array([0.0, 1.0, 0.0])
            }
        ]

    def create_valid_chunk(self, embedding):
        return {
            "source": "research_paper.pdf",
            "page": 1,
            "text": "Example research passage.",
            "embedding": embedding,
        }

    def test_builds_index_and_preserves_chunks(self):
        index, stored_chunks = build_faiss_index(self.chunks)

        self.assertEqual(index.ntotal, 2)
        self.assertEqual(index.d, 3)
        self.assertEqual(stored_chunks, self.chunks)

    def test_rejects_non_list_input(self):
        with self.assertRaises(TypeError):
            build_faiss_index(None)

    def test_rejects_empty_chunks(self):
        with self.assertRaises(ValueError):
            build_faiss_index([])

    def test_rejects_non_dictionary_chunk(self):
        with self.assertRaises(TypeError):
            build_faiss_index(["invalid chunk"])

    def test_rejects_missing_embedding(self):
        with self.assertRaises(ValueError):
            build_faiss_index([
                {"text": "Research passage"}
            ])

    def test_rejects_invalid_embedding_type(self):
        with self.assertRaises(TypeError):
            build_faiss_index([
                {"embedding": "invalid"}
            ])

    def test_rejects_non_numeric_embedding(self):
        with self.assertRaises(TypeError):
            build_faiss_index([
                self.create_valid_chunk(["invalid", "data"])
            ])

    def test_rejects_multidimensional_embedding(self):
        with self.assertRaises(ValueError):
            build_faiss_index([
                {"embedding": np.array([[1.0, 0.0]])}
            ])

    def test_rejects_empty_embedding(self):
        with self.assertRaises(ValueError):
            build_faiss_index([
                {"embedding": np.array([])}
            ])

    def test_rejects_inconsistent_embedding_dimensions(self):
        with self.assertRaises(ValueError):
            build_faiss_index([
                {"embedding": np.array([1.0, 0.0])},
                {"embedding": np.array([1.0, 0.0, 0.0])}
            ])

    def test_rejects_non_finite_embedding_values(self):
        invalid_vectors = [
            np.array([np.nan, 0.0]),
            np.array([np.inf, 0.0]),
            np.array([-np.inf, 0.0])
        ]

        for vector in invalid_vectors:
            with self.subTest(vector=vector):
                with self.assertRaises(ValueError):
                    build_faiss_index([
                        {"embedding": vector}
                    ])

    def test_rejects_zero_embedding(self):
        with self.assertRaises(ValueError):
            build_faiss_index([
                {"embedding": np.array([0.0, 0.0])}
            ])

    def test_normalizes_document_embeddings(self):
        chunks = [
            {"embedding": np.array([3.0, 4.0])},
            {"embedding": np.array([0.0, 5.0])}
        ]

        index, _ = build_faiss_index(chunks)

        reconstructed = np.zeros((2, 2), dtype=np.float32)
        index.reconstruct_n(0, 2, reconstructed)

        norms = np.linalg.norm(reconstructed, axis=1)

        np.testing.assert_allclose(
            norms,
            np.array([1.0, 1.0]),
            atol=1e-6
        )

    
    def test_accepts_list_tuple_and_numpy_embeddings(self):
        chunks = [
            self.create_valid_chunk([1.0, 0.0]),
            self.create_valid_chunk((0.0, 1.0)),
            self.create_valid_chunk(np.array([1.0, 1.0])),
        ]

        index, stored_chunks = build_faiss_index(chunks)

        self.assertEqual(index.ntotal, 3)
        self.assertEqual(len(stored_chunks), 3)

    def test_normalizes_document_embeddings(self):
        chunks = [
            self.create_valid_chunk(np.array([3.0, 4.0])),
            self.create_valid_chunk(np.array([0.0, 5.0])),
        ]

        index, _ = build_faiss_index(chunks)

        reconstructed = np.zeros((2, 2), dtype=np.float32)
        index.reconstruct_n(0, 2, reconstructed)

        norms = np.linalg.norm(reconstructed, axis=1)

        np.testing.assert_allclose(
            norms,
            np.array([1.0, 1.0]),
            atol=1e-6,
        )

    def test_rejects_invalid_embedding_type(self):
        with self.assertRaises(TypeError):
            build_faiss_index([
                self.create_valid_chunk("invalid")
            ])

    
class TestSearchChunks(unittest.TestCase):

    def setUp(self):
        self.chunks = [
            {
                "source": "paper1.pdf",
                "page": 1,
                "text": "Machine learning research",
                "embedding": np.array([1.0, 0.0])
            },
            {
                "source": "paper2.pdf",
                "page": 2,
                "text": "Deep learning research",
                "embedding": np.array([0.0, 1.0])
            },
            {
                "source": "paper3.pdf",
                "page": 3,
                "text": "Natural language processing",
                "embedding": np.array([0.7, 0.7])
            }
        ]

        self.index, self.stored_chunks = build_faiss_index(
            self.chunks
        )

    def create_valid_chunk(self, embedding):
        return {
            "source": "research_paper.pdf",
            "page": 1,
            "text": "Example research passage.",
            "embedding": embedding,
        }
    
    def test_returns_most_similar_chunk_first(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([1.0, 0.0]),
            top_k=3
        )

        self.assertEqual(
            results[0]["text"],
            "Machine learning research"
        )

    def test_returns_requested_number_of_results(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([1.0, 0.0]),
            top_k=2
        )

        self.assertEqual(len(results), 2)

    def test_returns_all_results_when_top_k_exceeds_index_size(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([1.0, 0.0]),
            top_k=10
        )

        self.assertEqual(len(results), 3)

    def test_returns_similarity_scores(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([1.0, 0.0])
        )

        for result in results:
            self.assertIn("score", result)
            self.assertIsInstance(result["score"], float)

    def test_preserves_chunk_metadata(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([1.0, 0.0])
        )

        self.assertIn("source", results[0])
        self.assertIn("page", results[0])
        self.assertIn("text", results[0])

    def test_rejects_boolean_top_k(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([1.0, 0.0]),
                top_k=True
            )

    def test_rejects_float_top_k(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([1.0, 0.0]),
                top_k=2.5
            )

    def test_rejects_string_top_k(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([1.0, 0.0]),
                top_k="2"
            )

    def test_rejects_non_positive_top_k(self):
        for value in [0, -1]:
            with self.subTest(top_k=value):
                with self.assertRaises(ValueError):
                    search_chunks(
                        self.index,
                        self.stored_chunks,
                        np.array([1.0, 0.0]),
                        top_k=value
                    )

    def test_rejects_invalid_index(self):
        with self.assertRaises(TypeError):
            search_chunks(
                None,
                self.stored_chunks,
                np.array([1.0, 0.0])
            )

    def test_rejects_non_list_stored_chunks(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                None,
                np.array([1.0, 0.0])
            )

    def test_rejects_non_dictionary_chunks(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                ["invalid chunk"] * 3,
                np.array([1.0, 0.0])
            )

    def test_rejects_index_chunk_count_mismatch(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks[:2],
                np.array([1.0, 0.0])
            )

    def test_empty_index_returns_empty_results(self):
        empty_index = faiss.IndexFlatIP(2)

        results = search_chunks(
            empty_index,
            [],
            np.array([1.0, 0.0])
        )

        self.assertEqual(results, [])

    def test_rejects_non_numeric_query(self):
        with self.assertRaises(TypeError):
            search_chunks(
                self.index,
                self.stored_chunks,
                ["invalid", "query"]
            )

    def test_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([])
            )

    def test_rejects_multiple_query_vectors(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([
                    [1.0, 0.0],
                    [0.0, 1.0]
                ])
            )

    def test_rejects_wrong_query_dimension(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([1.0, 0.0, 0.0])
            )

    def test_rejects_nan_query_embedding(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([np.nan, 0.0])
            )

    def test_rejects_infinite_query_embedding(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([np.inf, 0.0])
            )

    def test_rejects_zero_query_embedding(self):
        with self.assertRaises(ValueError):
            search_chunks(
                self.index,
                self.stored_chunks,
                np.array([0.0, 0.0])
            )

    def test_normalizes_query_before_search(self):
        results = search_chunks(
            self.index,
            self.stored_chunks,
            np.array([10.0, 0.0]),
            top_k=1
        )

        self.assertAlmostEqual(
            results[0]["score"],
            1.0,
            places=6
        )


if __name__ == "__main__":
    unittest.main()

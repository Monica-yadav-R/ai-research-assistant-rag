import faiss
import numpy as np
import pytest

from vector_store import search_chunks
from unittest.mock import patch

def create_valid_chunk(
    source="climate_study.pdf",
    page=1,
    text="Rising temperatures affect crop productivity.",
):
    return {
        "source": source,
        "page": page,
        "text": text,
    }


def create_test_index():
    # Three 2-dimensional document embeddings.
    vectors = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.8, 0.6],
        ],
        dtype=np.float32,
    )

    # Normalize the document embeddings.
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(2)
    index.add(vectors)

    chunks = [
        create_valid_chunk("paper1.pdf", 1, "Climate change affects crops."),
        create_valid_chunk("paper2.pdf", 2, "Rainfall affects agriculture."),
        create_valid_chunk("paper3.pdf", 3, "Temperature influences crop yield."),
    ]

    return index, chunks

def test_returns_top_k_results():
    index, chunks = create_test_index()

    results = search_chunks(
        index,
        chunks,
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=2,
    )

    assert len(results) == 2


def test_results_are_ranked_by_similarity():
    index, chunks = create_test_index()

    results = search_chunks(
        index,
        chunks,
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=3,
    )

    assert results[0]["source"] == "paper1.pdf"
    assert results[1]["source"] == "paper3.pdf"
    assert results[2]["source"] == "paper2.pdf"


def test_similarity_scores_are_descending():
    index, chunks = create_test_index()

    results = search_chunks(
        index,
        chunks,
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=3,
    )

    scores = [result["score"] for result in results]

    assert scores == sorted(scores, reverse=True)


def test_result_contains_original_metadata_and_score():
    index, chunks = create_test_index()

    results = search_chunks(
        index,
        chunks,
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=1,
    )

    result = results[0]

    assert result["source"] == "paper1.pdf"
    assert result["page"] == 1
    assert result["text"] == "Climate change affects crops."
    assert isinstance(result["score"], float)


def test_top_k_larger_than_index_returns_all_chunks():
    index, chunks = create_test_index()

    results = search_chunks(
        index,
        chunks,
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=10,
    )

    assert len(results) == 3


def test_empty_index_returns_empty_list():
    index = faiss.IndexFlatIP(2)

    results = search_chunks(
        index,
        [],
        np.array([1.0, 0.0], dtype=np.float32),
    )

    assert results == []

@pytest.mark.parametrize("top_k", [0, -1, -5])
def test_rejects_non_positive_top_k(top_k):
    index, chunks = create_test_index()

    with pytest.raises(ValueError):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
            top_k=top_k,
        )


@pytest.mark.parametrize("top_k", [1.5, "3", None, True])
def test_rejects_invalid_top_k_type(top_k):
    index, chunks = create_test_index()

    with pytest.raises(TypeError):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
            top_k=top_k,
        )


def test_rejects_non_faiss_index():
    _, chunks = create_test_index()

    with pytest.raises(TypeError):
        search_chunks(
            "not_an_index",
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
        )


def test_rejects_l2_index():
    index = faiss.IndexFlatL2(2)
    index.add(np.array([[1.0, 0.0]], dtype=np.float32))

    chunks = [create_valid_chunk()]

    with pytest.raises(ValueError, match="inner-product"):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
        )


def test_rejects_index_with_wrong_query_dimension():
    index, chunks = create_test_index()

    with pytest.raises(ValueError, match="dimension"):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0, 0.5], dtype=np.float32),
        )

def test_rejects_non_list_stored_chunks():
    index, _ = create_test_index()

    with pytest.raises(TypeError):
        search_chunks(
            index,
            "not_a_list",
            np.array([1.0, 0.0], dtype=np.float32),
        )


def test_rejects_non_dictionary_chunk():
    index, _ = create_test_index()

    with pytest.raises(TypeError):
        search_chunks(
            index,
            ["not_a_dictionary"] * 3,
            np.array([1.0, 0.0], dtype=np.float32),
        )


@pytest.mark.parametrize(
    "invalid_chunk",
    [
        {"page": 1, "text": "Some text"},
        {"source": "paper.pdf", "text": "Some text"},
        {"source": "paper.pdf", "page": 1},
        {"source": "", "page": 1, "text": "Some text"},
        {"source": "paper.pdf", "page": 0, "text": "Some text"},
        {"source": "paper.pdf", "page": -1, "text": "Some text"},
        {"source": "paper.pdf", "page": True, "text": "Some text"},
        {"source": "paper.pdf", "page": "1", "text": "Some text"},
        {"source": "paper.pdf", "page": 1, "text": ""},
        {"source": "paper.pdf", "page": 1, "text": "   "},
    ],
)
def test_rejects_invalid_chunk_metadata(invalid_chunk):
    index, chunks = create_test_index()

    chunks[0] = invalid_chunk

    with pytest.raises((TypeError, ValueError)):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
        )


def test_rejects_index_and_chunk_count_mismatch():
    index, chunks = create_test_index()

    chunks.pop()

    with pytest.raises(ValueError, match="not aligned"):
        search_chunks(
            index,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
        )


@pytest.mark.parametrize(
    "query",
    [
        [],
        [[1.0, 0.0], [0.0, 1.0]],
        [[[1.0, 0.0]]],
    ],
)
def test_rejects_invalid_query_shapes(query):
    index, chunks = create_test_index()

    with pytest.raises(ValueError):
        search_chunks(index, chunks, query)


@pytest.mark.parametrize(
    "query",
    [
        [1.0, 2.0, 3.0],
        [1.0],
    ],
)
def test_rejects_query_dimension_mismatch(query):
    index, chunks = create_test_index()

    with pytest.raises(ValueError, match="dimension"):
        search_chunks(index, chunks, query)


@pytest.mark.parametrize(
    "query",
    [
        [np.nan, 1.0],
        [np.inf, 1.0],
        [-np.inf, 1.0],
    ],
)
def test_rejects_non_finite_query_values(query):
    index, chunks = create_test_index()

    with pytest.raises(ValueError, match="finite"):
        search_chunks(index, chunks, query)


def test_rejects_zero_query_vector():
    index, chunks = create_test_index()

    with pytest.raises(ValueError, match="zero vector"):
        search_chunks(
            index,
            chunks,
            np.array([0.0, 0.0], dtype=np.float32),
        )


def test_rejects_non_numeric_query():
    index, chunks = create_test_index()

    with pytest.raises(TypeError, match="numeric"):
        search_chunks(index, chunks, ["hello", "world"])

def test_rejects_invalid_faiss_chunk_id():
    index = faiss.IndexFlatIP(2)
    index.add(
        np.array([[1.0, 0.0]], dtype=np.float32)
    )

    chunks = [create_valid_chunk()]

    fake_scores = np.array([[0.9]], dtype=np.float32)
    fake_ids = np.array([[5]], dtype=np.int64)

    with patch.object(
        index,
        "search",
        return_value=(fake_scores, fake_ids),
    ):
        with pytest.raises(RuntimeError, match="invalid chunk ID"):
            search_chunks(
                index,
                chunks,
                np.array([1.0, 0.0], dtype=np.float32),
            )

@pytest.mark.parametrize("score", [np.nan, np.inf, -np.inf])
def test_rejects_non_finite_faiss_score(score):
    index = faiss.IndexFlatIP(2)
    index.add(
        np.array([[1.0, 0.0]], dtype=np.float32)
    )

    chunks = [create_valid_chunk()]

    fake_scores = np.array([[score]], dtype=np.float32)
    fake_ids = np.array([[0]], dtype=np.int64)

    with patch.object(
        index,
        "search",
        return_value=(fake_scores, fake_ids),
    ):
        with pytest.raises(RuntimeError, match="non-finite"):
            search_chunks(
                index,
                chunks,
                np.array([1.0, 0.0], dtype=np.float32),
            )

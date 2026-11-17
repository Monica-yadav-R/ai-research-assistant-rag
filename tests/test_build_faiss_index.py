
import numpy as np
import pytest
import faiss

import vector_store
from vector_store import build_faiss_index


# --------------------------------------------------
# Helper function: Create valid embedded chunks
# --------------------------------------------------
_DEFAULT_EMBEDDING = object()


def create_valid_chunk(
    source="climate_study.pdf",
    page=1,
    text="Rising temperatures affect crop productivity.",
    embedding=_DEFAULT_EMBEDDING,
):
    if embedding is _DEFAULT_EMBEDDING:
        embedding = [0.3, 0.4, 0.5]

    return {
        "source": source,
        "page": page,
        "text": text,
        "embedding": embedding,
    }
# --------------------------------------------------
# 1. Valid input tests
# --------------------------------------------------

def test_build_faiss_index_with_valid_chunks():

    chunks = [
        create_valid_chunk(embedding=[0.3, 0.4, 0.5]),
        create_valid_chunk(
            source="agriculture.pdf",
            page=2,
            text="Climate change affects agriculture.",
            embedding=[0.6, 0.7, 0.8],
        ),
    ]

    index, stored_chunks = build_faiss_index(chunks)

    assert isinstance(index, faiss.Index)
    assert index.ntotal == 2
    assert len(stored_chunks) == 2


def test_build_faiss_index_preserves_chunk_order():

    chunks = [
        create_valid_chunk(page=1),
        create_valid_chunk(page=2),
        create_valid_chunk(page=3),
    ]

    index, stored_chunks = build_faiss_index(chunks)

    assert index.ntotal == 3
    assert stored_chunks == chunks

    assert stored_chunks[0]["page"] == 1
    assert stored_chunks[1]["page"] == 2
    assert stored_chunks[2]["page"] == 3


def test_build_faiss_index_supports_numpy_embeddings():

    chunks = [
        create_valid_chunk(
            embedding=np.array([0.3, 0.4, 0.5])
        )
    ]

    index, stored_chunks = build_faiss_index(chunks)

    assert index.ntotal == 1
    assert len(stored_chunks) == 1


def test_build_faiss_index_supports_tuple_embeddings():

    chunks = [
        create_valid_chunk(
            embedding=(0.3, 0.4, 0.5)
        )
    ]

    index, stored_chunks = build_faiss_index(chunks)

    assert index.ntotal == 1


# --------------------------------------------------
# 2. Input collection validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        "invalid",
        {},
        123,
        (create_valid_chunk(),),
    ],
)
def test_build_faiss_index_rejects_non_list_input(invalid_input):

    with pytest.raises(TypeError):
        build_faiss_index(invalid_input)


def test_build_faiss_index_rejects_empty_list():

    with pytest.raises(ValueError):
        build_faiss_index([])


# --------------------------------------------------
# 3. Chunk validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_chunk",
    [
        None,
        "invalid chunk",
        123,
        [],
    ],
)
def test_build_faiss_index_rejects_non_dictionary_chunks(invalid_chunk):

    with pytest.raises(TypeError):
        build_faiss_index([invalid_chunk])


@pytest.mark.parametrize(
    "missing_field",
    ["source", "page", "text", "embedding"],
)
def test_build_faiss_index_rejects_missing_chunk_fields(missing_field):

    chunk = create_valid_chunk()
    del chunk[missing_field]

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 4. Source metadata validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_source",
    [
        "",
        "   ",
        None,
        123,
        [],
    ],
)
def test_build_faiss_index_rejects_invalid_source(invalid_source):

    chunk = create_valid_chunk(source=invalid_source)

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 5. Page metadata validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_page",
    [
        True,
        False,
        "1",
        1.5,
        None,
        [],
    ],
)
def test_build_faiss_index_rejects_non_integer_page(invalid_page):

    chunk = create_valid_chunk(page=invalid_page)

    with pytest.raises(TypeError):
        build_faiss_index([chunk])


@pytest.mark.parametrize(
    "invalid_page",
    [0, -1, -5],
)
def test_build_faiss_index_rejects_non_positive_page(invalid_page):

    chunk = create_valid_chunk(page=invalid_page)

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 6. Text metadata validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_text",
    [
        "",
        "   ",
        None,
        123,
        [],
    ],
)
def test_build_faiss_index_rejects_invalid_text(invalid_text):

    chunk = create_valid_chunk(text=invalid_text)

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 7. Embedding type validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_embedding",
    [
        None,
        "not an embedding",
        123,
        {},
        set([0.3, 0.4, 0.5]),
    ],
)
def test_build_faiss_index_rejects_unsupported_embedding_type(
    invalid_embedding,
):

    chunk = create_valid_chunk(embedding=invalid_embedding)

    with pytest.raises(TypeError):
        build_faiss_index([chunk])


def test_build_faiss_index_rejects_non_numeric_embedding():

    chunk = create_valid_chunk(
        embedding=["a", "b", "c"]
    )

    with pytest.raises(TypeError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 8. Embedding dimension validation
# --------------------------------------------------

def test_build_faiss_index_rejects_two_dimensional_embedding():

    chunk = create_valid_chunk(
        embedding=[[0.3, 0.4, 0.5]]
    )

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


def test_build_faiss_index_rejects_empty_embedding():

    chunk = create_valid_chunk(embedding=[])

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


def test_build_faiss_index_rejects_inconsistent_dimensions():

    chunks = [
        create_valid_chunk(embedding=[0.3, 0.4, 0.5]),
        create_valid_chunk(embedding=[0.6, 0.7]),
    ]

    with pytest.raises(ValueError):
        build_faiss_index(chunks)


# --------------------------------------------------
# 9. Numerical validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_embedding",
    [
        [np.nan, 0.4, 0.5],
        [0.3, np.inf, 0.5],
        [0.3, 0.4, -np.inf],
    ],
)
def test_build_faiss_index_rejects_non_finite_embeddings(
    invalid_embedding,
):

    chunk = create_valid_chunk(embedding=invalid_embedding)

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


def test_build_faiss_index_rejects_zero_vector():

    chunk = create_valid_chunk(
        embedding=[0.0, 0.0, 0.0]
    )

    with pytest.raises(ValueError):
        build_faiss_index([chunk])


# --------------------------------------------------
# 10. Normalization tests
# --------------------------------------------------

def test_build_faiss_index_normalizes_vectors():

    chunks = [
        create_valid_chunk(embedding=[3.0, 4.0, 0.0])
    ]

    index, _ = build_faiss_index(chunks)

    normalized_vector = index.reconstruct(0)

    expected_vector = np.array(
        [0.6, 0.8, 0.0],
        dtype=np.float32,
    )

    assert np.allclose(
        normalized_vector,
        expected_vector,
        atol=1e-6,
    )


def test_build_faiss_index_normalizes_each_vector_independently():

    chunks = [
        create_valid_chunk(embedding=[3.0, 4.0, 0.0]),
        create_valid_chunk(embedding=[0.0, 5.0, 12.0]),
    ]

    index, _ = build_faiss_index(chunks)

    first_vector = index.reconstruct(0)
    second_vector = index.reconstruct(1)

    assert np.isclose(np.linalg.norm(first_vector), 1.0)
    assert np.isclose(np.linalg.norm(second_vector), 1.0)


# --------------------------------------------------
# 11. FAISS index correctness
# --------------------------------------------------

def test_build_faiss_index_uses_inner_product_metric():

    chunks = [create_valid_chunk()]

    index, _ = build_faiss_index(chunks)

    assert index.metric_type == faiss.METRIC_INNER_PRODUCT


def test_build_faiss_index_uses_correct_dimension():

    chunks = [
        create_valid_chunk(embedding=[0.3, 0.4, 0.5, 0.6])
    ]

    index, _ = build_faiss_index(chunks)

    assert index.d == 4


def test_build_faiss_index_keeps_vector_count_aligned():

    chunks = [
        create_valid_chunk(),
        create_valid_chunk(page=2),
        create_valid_chunk(page=3),
    ]

    index, stored_chunks = build_faiss_index(chunks)

    assert index.ntotal == len(stored_chunks)


# --------------------------------------------------
# 12. Defensive index-count verification
# --------------------------------------------------

def test_build_faiss_index_raises_if_faiss_adds_wrong_count(
    monkeypatch,
):

    class FakeIndex:

        def __init__(self, dimension):
            self.d = dimension
            self.ntotal = 0

        def add(self, vectors):
            # Simulate an index that fails to store vectors.
            self.ntotal = 0

    monkeypatch.setattr(
        vector_store.faiss,
        "IndexFlatIP",
        FakeIndex,
    )

    chunks = [create_valid_chunk()]

    with pytest.raises(RuntimeError):
        build_faiss_index(chunks)

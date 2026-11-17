
import faiss
import numpy as np
from pathlib import Path
import json

def build_faiss_index(
    embedded_chunks: list[dict],
) -> tuple[faiss.Index, list[dict]]:

    # 1. Validate the input collection
    if not isinstance(embedded_chunks, list):
        raise TypeError("Embedded chunks must be a list")

    if not embedded_chunks:
        raise ValueError("Cannot build an index without embedded chunks")

    vectors_list = []
    expected_dimension = None

    # 2. Validate each chunk and its embedding
    for position, chunk in enumerate(embedded_chunks):

        if not isinstance(chunk, dict):
            raise TypeError(
                f"Chunk at position {position} must be a dictionary"
            )

        if "source" not in chunk:
            raise ValueError(
                f"Chunk at position {position} is missing 'source' name."
            )
        
        if "page" not in chunk:
            raise ValueError(
                f"Chunk at position {position} is missing 'page number'."
            )
        if "text" not in chunk:
            raise ValueError(
                f"Chunk at position {position} has missing 'text'."
            )
        
        if not isinstance(chunk["source"], str) or not chunk["source"].strip():
            raise ValueError(
                f"Chunk at position {position} must have a non-empty source"
            )

        if isinstance(chunk["page"], bool) or not isinstance(chunk["page"], int):
            raise TypeError(
                f"Page number at position {position} must be an integer"
            )

        if chunk["page"] <= 0:
            raise ValueError(
                f"Page number at position {position} must be positive"
            )

        if not isinstance(chunk["text"], str) or not chunk["text"].strip():
            raise ValueError(
                f"Chunk at position {position} must have non-empty text"
            )
        
        if "embedding" not in chunk:
            raise ValueError(
                f"Chunk at position {position} is missing 'embedding'"
            )

        embedding = chunk["embedding"]

        # 3. Accept lists, tuples, and NumPy arrays
        if not isinstance(embedding, (list, tuple, np.ndarray)):
            raise TypeError(
                f"Embedding at position {position} must be a list, "
                "tuple, or NumPy array"
            )

        # 4. Convert to a NumPy array
        try:
            vector = np.asarray(embedding, dtype=np.float32)
        except (TypeError, ValueError) as error:
            raise TypeError(
                f"Embedding at position {position} must contain numeric values"
            ) from error

        # 5. Validate embedding dimensions
        if vector.ndim != 1:
            raise ValueError(
                f"Embedding at position {position} must be one-dimensional"
            )

        if vector.size == 0:
            raise ValueError(
                f"Embedding at position {position} cannot be empty"
            )

        # 6. Establish and enforce consistent dimensions
        if expected_dimension is None:
            expected_dimension = vector.size

        elif vector.size != expected_dimension:
            raise ValueError(
                "All embeddings must have the same dimension"
            )

        # 7. Validate numerical values
        if not np.isfinite(vector).all():
            raise ValueError(
                f"Embedding at position {position} must contain only finite numbers"
            )

        vectors_list.append(vector)

    # 8. Combine individual vectors into a 2D matrix
    vectors = np.vstack(vectors_list)

    # 9. Reject zero vectors
    norms = np.linalg.norm(vectors.astype(np.float64), axis=1)
    # calculates each vector's magnitude row by row

    if np.any(norms == 0):
        raise ValueError("Embeddings cannot contain zero vectors")

    # 10. Normalize document embeddings
    vectors = (
        vectors.astype(np.float64) / norms[:, np.newaxis]
    ).astype(np.float32)
    # Reshape norms for broadcasting, normalize each vector,
    # and convert the resulting matrix to float32.

    # 11. Build FAISS inner-product index
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    if index.ntotal != len(embedded_chunks):
        raise RuntimeError(
            "FAISS index and stored chunks are misaligned"
        )
    
    return index, list(embedded_chunks)


def search_chunks(
    index: faiss.Index,
    stored_chunks: list[dict],
    query_embedding: np.ndarray,
    top_k: int = 3,
) -> list[dict]:

    # 1. Validate top_k
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise TypeError("top_k must be an integer")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    # 2. Validate FAISS index
    if not isinstance(index, faiss.Index):
        raise TypeError("index must be a FAISS index")

    if index.metric_type != faiss.METRIC_INNER_PRODUCT:
        raise ValueError(
            "FAISS index must use inner-product similarity"
        )

    if index.d <= 0:
        raise ValueError("FAISS index dimension must be greater than 0")

    # 3. Validate stored chunks
    if not isinstance(stored_chunks, list):
        raise TypeError("stored_chunks must be a list")

    if any(not isinstance(chunk, dict) for chunk in stored_chunks):
        raise TypeError("Every stored chunk must be a dictionary")

    for position, chunk in enumerate(stored_chunks):

        if "source" not in chunk:
            raise ValueError(f"Chunk at position {position} is missing 'source'")

        if not isinstance(chunk["source"], str) or not chunk["source"].strip():
            raise ValueError(f"Chunk at position {position} must have a non-empty source")

        if "page" not in chunk:
            raise ValueError(f"Chunk at position {position} is missing 'page'")

        if isinstance(chunk["page"], bool) or not isinstance(chunk["page"], int):
            raise TypeError(f"Page at position {position} must be an integer")

        if chunk["page"] <= 0:
            raise ValueError(f"Page at position {position} must be positive")

        if "text" not in chunk:
            raise ValueError(f"Chunk at position {position} is missing 'text'")

        if not isinstance(chunk["text"], str) or not chunk["text"].strip():
            raise ValueError(f"Chunk at position {position} must have non-empty text")

    
    if index.ntotal != len(stored_chunks):
        raise ValueError("Index and stored chunks are not aligned")

    if index.ntotal == 0:
        return []

    # 4. Convert query embedding
    try:
        query = np.asarray(query_embedding, dtype=np.float32)
    except (TypeError, ValueError) as error:
        raise TypeError(
            "Query embedding must contain numeric values"
        ) from error

    # 5. Validate query shape
    if query.size == 0:
        raise ValueError("Query embedding cannot be empty")

    if query.ndim == 1:
        query = query.reshape(1, -1)

    if query.ndim != 2 or query.shape[0] != 1:
        raise ValueError("Query embedding must contain one vector")

    if query.shape[1] != index.d:
        raise ValueError(
            "Query embedding dimension must match index dimension"
        )

    # 6. Validate numerical values
    if not np.isfinite(query).all():
        raise ValueError(
            "Query embedding must contain only finite numbers"
        )

    # 7. Normalize query embedding
    norm = np.linalg.norm(query.astype(np.float64))

    if norm == 0:
        raise ValueError("Query embedding cannot be a zero vector")

    query = (query.astype(np.float64) / norm).astype(np.float32)

    # 8. Search FAISS index
    scores, ids = index.search(
        query,
        min(top_k, index.ntotal)
    )

    # 9. Construct retrieval results
    results = []

    for score, chunk_id in zip(scores[0], ids[0]):

        if chunk_id < 0:
            continue

        if chunk_id >= len(stored_chunks):
            raise RuntimeError("FAISS returned an invalid chunk ID")

        if not np.isfinite(score):
            raise RuntimeError(
                "FAISS returned a non-finite similarity score"
            )
        
        result = dict(stored_chunks[int(chunk_id)])
        result["score"] = float(score)

        results.append(result)

    return results

def get_vector_store_paths(storage_dir):
    storage_dir = Path(storage_dir)
    index_path = storage_dir / "index.faiss"
    metadata_path = storage_dir / "chunks.json"
    return index_path, metadata_path

def save_vector_store(index,stored_chunks,storage_dir):
    storage_dir = Path(storage_dir)
    if index.ntotal != len(stored_chunks):
        raise ValueError(
            "The number of FAISS vectors and metadata records must match."
        )
    storage_dir.mkdir(parents=True, exist_ok=True)
    index_path ,metadata_path = get_vector_store_paths(storage_dir)
    metadata = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "text": chunk["text"]
        }
        for chunk in stored_chunks
    ]
    faiss.write_index(index,str(index_path))
    with open(metadata_path,"w",encoding="utf-8") as file:
        json.dump(metadata,file,indent=4)
    return index_path,metadata_path

def load_vector_store(storage_dir):
    index_path ,metadata_path = get_vector_store_paths(storage_dir)
    if not index_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Vector store files are missing.")
    index = faiss.read_index(str(index_path))
    with open(metadata_path,"r",encoding="utf-8") as file:
        stored_chunks = json.load(file)
    if not isinstance(stored_chunks, list):
        raise ValueError("Stored metadata must be a list.")
    if index.ntotal != len(stored_chunks):
        raise ValueError(
            "The number of FAISS vectors and metadata records must match."      
        )
    return index,stored_chunks
import sys
from pathlib import Path

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import chromadb

from api.chroma_store import delete_document_chunks


# Create an isolated, temporary ChromaDB collection
client = chromadb.EphemeralClient()

collection = client.create_collection(
    name="delete_test"
)

# Add chunks belonging to two different documents
collection.add(
    ids=["docA_0", "docA_1", "docB_0", "docA_userB_0"],
    embeddings=[
        [0.1] * 384,
        [0.2] * 384,
        [0.3] * 384,
        [0.4] * 384
    ],
    documents=[
        "First chunk",
        "Second chunk",
        "Another document's chunk",
        "Same document ID, different user"
    ],
    metadatas=[
        {"document_id": "docA", "user_id": "userA"},
        {"document_id": "docA", "user_id": "userA"},
        {"document_id": "docB", "user_id": "userA"},
        {"document_id": "docA", "user_id": "userB"}
    ]
)

# Delete only document A
deleted_count = delete_document_chunks(
    collection,
    document_id="docA",
    user_id="userA"
)
# Verify remaining chunks
remaining = collection.get()

assert deleted_count == 2

assert set(remaining["ids"]) == {
    "docB_0",
    "docA_userB_0"
}

print("Deleted chunks:", deleted_count)
print("Remaining chunks:", remaining["ids"])
print("User isolation verified.")
print("ChromaDB deletion test passed!")
print("Deleted chunks:", deleted_count)
print("Remaining chunks:", remaining["ids"])
print("ChromaDB deletion test passed!")

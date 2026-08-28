import os
import chromadb


# --------------------------------
# ChromaDB configuration
# --------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = "knowledge_base"


# --------------------------------
# Create ChromaDB client
# --------------------------------

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)


# --------------------------------
# Get or create collection
# --------------------------------

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# --------------------------------
# Add documents
# --------------------------------

def add_documents(
    documents,
    embeddings,
    metadatas,
    ids
):
    """
    Add document chunks, embeddings,
    metadata and IDs to ChromaDB.
    """

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


# --------------------------------
# Search documents
# --------------------------------

def search_documents(
    query_embedding,
    n_results=3
):
    """
    Search ChromaDB for documents
    similar to the query.
    """

    # Avoid requesting more results
    # than actually exist.
    total_documents = collection.count()

    if total_documents == 0:
        return {
            "documents": [[]],
            "metadatas": [[]]
        }

    n_results = min(
        n_results,
        total_documents
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


# --------------------------------
# Get number of stored chunks
# --------------------------------

def get_collection_count():

    return collection.count()

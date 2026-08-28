import chromadb


# --------------------------------
# ChromaDB configuration
# --------------------------------

CHROMA_DIR = "chroma_db"

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
    n_results=5
):
    """
    Search ChromaDB for documents
    similar to the query.
    """

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
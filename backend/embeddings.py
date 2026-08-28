from sentence_transformers import SentenceTransformer


# --------------------------------
# Embedding model
# --------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


# --------------------------------
# Create embeddings for multiple texts
# --------------------------------

def create_embeddings(texts):
    """
    Convert a list of text chunks into embeddings.
    """

    embeddings = embedding_model.encode(texts)

    return embeddings.tolist()


# --------------------------------
# Create embedding for one text
# --------------------------------

def create_embedding(text):
    """
    Convert a single text/query into an embedding.
    """

    embedding = embedding_model.encode(text)

    return embedding.tolist()
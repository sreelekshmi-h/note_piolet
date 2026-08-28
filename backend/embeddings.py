from sentence_transformers import SentenceTransformer


# --------------------------------
# Embedding model configuration
# --------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

# Model will NOT be loaded immediately
embedding_model = None


# --------------------------------
# Load embedding model only when needed
# --------------------------------

def get_embedding_model():

    global embedding_model

    if embedding_model is None:

        print("Loading embedding model...")

        embedding_model = SentenceTransformer(
            MODEL_NAME
        )

        print("Embedding model loaded.")

    return embedding_model


# --------------------------------
# Create embeddings for multiple texts
# --------------------------------

def create_embeddings(texts):
    """
    Convert a list of text chunks into embeddings.
    """

    model = get_embedding_model()

    embeddings = model.encode(
        texts
    )

    return embeddings.tolist()


# --------------------------------
# Create embedding for one text
# --------------------------------

def create_embedding(text):
    """
    Convert a single text/query into an embedding.
    """

    model = get_embedding_model()

    embedding = model.encode(
        text
    )

    return embedding.tolist()

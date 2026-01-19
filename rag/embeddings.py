from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    """Get HuggingFace embeddings model"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

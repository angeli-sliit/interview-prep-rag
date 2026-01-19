from langchain_community.vectorstores import Chroma
import os

def create_vector_store(chunks, embeddings, persist_directory="db"):
    """Create or load vector store"""
    if os.path.exists(persist_directory):
        # Load existing vector store
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        # Create new vector store
        return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )

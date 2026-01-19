from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
import os

def load_pdf(path):
    """Load PDF document"""
    loader = PyPDFLoader(path)
    return loader.load()

def load_text(path):
    """Load text document"""
    loader = TextLoader(path)
    return loader.load()

def load_document(path):
    """Load document based on file extension"""
    if path.endswith('.pdf'):
        return load_pdf(path)
    elif path.endswith('.txt'):
        return load_text(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

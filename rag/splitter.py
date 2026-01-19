from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(docs, chunk_size=500, chunk_overlap=100):
    """Split documents into chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(docs)

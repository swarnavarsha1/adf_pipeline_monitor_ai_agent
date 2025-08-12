"""
Builds a FAISS index from PDFs in the knowledge_pdfs/ folder so the RAG retriever can use them.
Run this whenever you add/update PDFs:
    python rag/build_rag_index.py
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY

# Paths
PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_pdfs")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")

def build_index():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment or config.py")

    all_docs = []
    for fname in os.listdir(PDF_DIR):
        if not fname.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(PDF_DIR, fname)
        print(f"[RAG] Loading PDF: {fname}")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Split into manageable chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = splitter.split_documents(docs)

        # Record source metadata
        for d in split_docs:
            d.metadata['source_file'] = fname
        all_docs.extend(split_docs)

    print(f"[RAG] {len(all_docs)} total chunks extracted from PDFs.")

    # Create embeddings for all chunks
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(all_docs, embeddings)

    # Save the FAISS index to disk
    os.makedirs(INDEX_DIR, exist_ok=True)
    vectorstore.save_local(INDEX_DIR)
    print(f"[RAG] Index built and saved to {INDEX_DIR}")

if __name__ == "__main__":
    build_index()

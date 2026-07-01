# rag/indexer.py
# This file handles reading PDFs and storing them in our local Chroma vector database.

import os
from dotenv import load_dotenv

# Load .env file FIRST — must happen before importing ChromaDB
load_dotenv()

# Silence ChromaDB telemetry error messages (harmless but annoying)
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Folder where our vector database will be saved on disk
CHROMA_DB_PATH = "chroma_db"

# Free, local embedding model (downloads once, then runs offline)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model():
    """Load the free local embedding model (turns text into numbers)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def load_and_split_pdf(file_path: str):
    """
    Step 1: Read a PDF file.
    Step 2: Split it into small overlapping chunks (so AI can search them easily).
    """
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split big documents into ~1000 character chunks with 200 char overlap
        # Overlap helps prevent losing context at chunk boundaries
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)
        return chunks
    except Exception as e:
        print(f"❌ Error reading PDF {file_path}: {e}")
        return []


def index_documents(file_paths: list):
    """
    Main function: takes a list of PDF file paths, processes them,
    and saves them into the local Chroma vector database.
    """
    all_chunks = []
    for path in file_paths:
        chunks = load_and_split_pdf(path)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("⚠️ No content extracted from documents.")
        return None

    embeddings = get_embedding_model()

    # Create (or update) the local Chroma database with our chunks
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    print(f"✅ Indexed {len(all_chunks)} chunks from {len(file_paths)} document(s).")
    return vectorstore
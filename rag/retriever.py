# rag/retriever.py
# This file searches our local Chroma database for relevant document chunks.

import os
from dotenv import load_dotenv

# Load .env FIRST before importing ChromaDB — this silences telemetry errors
load_dotenv()
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

from langchain_chroma import Chroma
from rag.indexer import get_embedding_model, CHROMA_DB_PATH


def load_vectorstore():
    """Load the existing Chroma database from disk (if it exists)."""
    if not os.path.exists(CHROMA_DB_PATH):
        return None

    embeddings = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )
    return vectorstore


def retrieve_relevant_chunks(query: str, k: int = 4):
    """
    Search the database for the top 'k' chunks most relevant to the query.
    Returns a list of text chunks + their source info.
    """
    try:
        vectorstore = load_vectorstore()
        if vectorstore is None:
            return []

        results = vectorstore.similarity_search(query, k=k)

        formatted = []
        for doc in results:
            formatted.append({
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", "N/A")
            })
        return formatted
    except Exception as e:
        print(f"❌ Error retrieving chunks: {e}")
        return []
# src/retrieval/vector_store.py

import logging
import os
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# Use the recommended import path for Document
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# Get logger instance using standard practice
logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# DEFAULT_FAISS_INDEX_PATH = "./faiss_index" # Removed: No longer saving to disk

def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL) -> Optional[Embeddings]:
    """Initializes and returns HuggingFace embeddings.

    Args:
        model_name: The name of the sentence-transformer model to use.

    Returns:
        An Embeddings object or None if an error occurs.
    """
    try:
        logger.info(f"Initializing HuggingFace embedding model: {model_name}")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        logger.info("Initialized HuggingFace embeddings successfully.")
        return embeddings
    except Exception:
        logger.exception(f"Failed to initialize embedding model '{model_name}'")
        return None

def build_faiss_index(documents: List[Document]) -> Optional[FAISS]:
    """Builds a FAISS index from documents in memory.

    Args:
        documents: A list of LangChain Document objects.

    Returns:
        A FAISS index object if successful, None otherwise.
    """
    logger.info("Attempting to build FAISS index in memory...")
    embeddings = get_embedding_function()
    if not embeddings:
        logger.error("Cannot build FAISS index: Failed to get embedding function.")
        return None

    if not documents:
        logger.warning("Cannot build FAISS index: No documents provided.")
        return None

    try:
        logger.info(f"Building FAISS index from {len(documents)} documents...")
        faiss_index = FAISS.from_documents(documents, embeddings)
        logger.info("FAISS index built successfully in memory.")
        return faiss_index # Return the index object directly
    except Exception:
        logger.exception("Failed to build FAISS index from documents.")
        return None # Return None on failure

# Removed the try-except block for saving to disk and related logic/logging

# Removed load_faiss_index function entirely

def search_index(query: str, index: FAISS, top_k: int = 3) -> List[Document]:
    """Performs a similarity search on the provided FAISS index.

    Args:
        query: The query string.
        index: The in-memory FAISS index object.
        top_k: The number of top relevant documents to retrieve.

    Returns:
        A list of relevant Document objects, or an empty list on failure.
    """
    if not index:
        logger.error("Cannot search: Invalid or null FAISS index provided.")
        return []

    try:
        logger.info(f"Performing similarity search with top_k={top_k} for query: '{query[:100]}...'")
        results = index.similarity_search(query, k=top_k)
        logger.info(f"Similarity search completed. Found {len(results)} results.")
        return results
    except Exception:
        logger.exception("Error during similarity search execution.")
        return [] 
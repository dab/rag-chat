# src/retrieval/vector_store.py

import logging
import os
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_FAISS_INDEX_PATH = "./faiss_index" # Store index in the root directory for now

def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL) -> Optional[Embeddings]:
    """Initializes and returns HuggingFace embeddings.

    Args:
        model_name: The name of the sentence-transformer model to use.

    Returns:
        An Embeddings object or None if an error occurs.
    """
    try:
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        logger.info(f"Initialized HuggingFace embeddings with model: {model_name}")
        return embeddings
    except Exception as e:
        logger.exception(f"Failed to initialize embedding model '{model_name}': {e}")
        return None

def build_faiss_index(documents: List[Document], index_path: str = DEFAULT_FAISS_INDEX_PATH) -> bool:
    """Builds a FAISS index from documents and saves it locally.

    Args:
        documents: A list of LangChain Document objects.
        index_path: The path to save the FAISS index.

    Returns:
        True if index building and saving was successful, False otherwise.
    """
    embeddings = get_embedding_function()
    if not embeddings:
        logger.error("Cannot build FAISS index: Failed to get embedding function.")
        return False

    if not documents:
        logger.warning("Cannot build FAISS index: No documents provided.")
        return False

    try:
        logger.info(f"Building FAISS index from {len(documents)} documents...")
        faiss_index = FAISS.from_documents(documents, embeddings)
        logger.info("FAISS index built successfully.")
    except Exception as e:
        logger.exception(f"Failed to build FAISS index: {e}")
        return False

    try:
        logger.info(f"Saving FAISS index to: {index_path}")
        faiss_index.save_local(index_path)
        logger.info("FAISS index saved successfully.")
        return True
    except Exception as e:
        logger.exception(f"Failed to save FAISS index to '{index_path}': {e}")
        return False

def load_faiss_index(index_path: str = DEFAULT_FAISS_INDEX_PATH) -> Optional[FAISS]:
    """Loads a FAISS index from a local path.

    Args:
        index_path: The path where the FAISS index is saved.

    Returns:
        A loaded FAISS index object or None if loading fails.
    """
    required_files = [os.path.join(index_path, "index.faiss"), os.path.join(index_path, "index.pkl")]
    if not all(os.path.exists(f) for f in required_files):
        logger.error(f"FAISS index files not found in '{index_path}'. Required: index.faiss, index.pkl")
        return None

    embeddings = get_embedding_function()
    if not embeddings:
        logger.error("Cannot load FAISS index: Failed to get embedding function.")
        return None

    try:
        logger.info(f"Loading FAISS index from: {index_path}")
        # allow_dangerous_deserialization is required for FAISS with HuggingFaceEmbeddings
        faiss_index = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True 
        )
        logger.info("FAISS index loaded successfully.")
        return faiss_index
    except Exception as e:
        logger.exception(f"Failed to load FAISS index from '{index_path}': {e}")
        return None

def search_index(query: str, index: FAISS, top_k: int = 3) -> List[Document]:
    """Performs a similarity search on the FAISS index.

    Args:
        query: The query string.
        index: The loaded FAISS index object.
        top_k: The number of top relevant documents to retrieve.

    Returns:
        A list of relevant Document objects, or an empty list on failure.
    """
    if not index:
        logger.error("Cannot search: Invalid FAISS index provided.")
        return []
    
    try:
        logger.info(f"Performing similarity search for query: '{query}' with top_k={top_k}")
        results = index.similarity_search(query, k=top_k)
        logger.info(f"Found {len(results)} results.")
        return results
    except Exception as e:
        logger.exception(f"Error during similarity search: {e}")
        return [] 
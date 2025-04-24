# src/processing/pdf_processor.py

import logging
import tempfile
import os
from typing import List
# Use try-except for Streamlit import for compatibility if run outside Streamlit context
try:
    import streamlit as st
    # Get the actual UploadedFile type hint if possible
    from streamlit.runtime.uploaded_file_manager import UploadedFile
except ImportError:
    # Define a placeholder if Streamlit is not installed (e.g., for basic testing)
    # In a real scenario, this module is expected to run within a Streamlit app
    UploadedFile = object # type: ignore 

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Initialize logger
logger = logging.getLogger(__name__)

# Constants for chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def process_pdfs_to_documents(uploaded_files: List[UploadedFile]) -> List[Document]:
    """
    Processes uploaded PDF files into LangChain Document objects suitable for RAG.

    Uses PyPDFLoader to load documents and RecursiveCharacterTextSplitter to chunk them.
    Handles temporary file creation for PyPDFLoader and ensures cleanup.

    Args:
        uploaded_files: A list of Streamlit UploadedFile objects.

    Returns:
        A list of LangChain Document objects (chunks), or an empty list if processing fails.
    """
    all_split_docs: List[Document] = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    
    if not uploaded_files:
        logger.warning("No uploaded files provided to process_pdfs_to_documents.")
        return []

    logger.info(f"Starting processing for {len(uploaded_files)} PDF file(s).")

    for uploaded_file in uploaded_files:
        temp_file_path = None # Initialize path
        try:
            # Create a temporary file to store the uploaded PDF content
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name # Get the path
            
            logger.info(f"Processing '{uploaded_file.name}' (Temp path: {temp_file_path})...")

            # Use PyPDFLoader with the temporary file path
            loader = PyPDFLoader(temp_file_path)
            # Load and split the document into pages/chunks
            # load_and_split is efficient as it processes pages iteratively
            pages = loader.load_and_split(text_splitter=text_splitter) 
            
            logger.info(f"Successfully processed '{uploaded_file.name}', generated {len(pages)} chunks.")
            all_split_docs.extend(pages)

        except Exception as e:
            logger.exception(f"Failed to process PDF file '{uploaded_file.name}'. Error: {e}")
            # Optionally, you could surface this error to the Streamlit UI
            # For now, just log and continue with other files
            continue 
        finally:
            # Ensure temporary file is deleted even if an error occurs
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"Successfully removed temporary file: {temp_file_path}")
                except Exception as e:
                    logger.error(f"Error removing temporary file '{temp_file_path}': {e}")

    logger.info(f"Finished processing. Total chunks generated: {len(all_split_docs)}.")
    return all_split_docs 
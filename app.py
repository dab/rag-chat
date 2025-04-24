import streamlit as st
import logging
import sys
import os
from dotenv import load_dotenv
from src.processing.query_processor import process_query
from src.retrieval.vector_store import build_faiss_index, search_index
from src.generation.answer_generator import generate_answer
from src.config.logging_config import setup_logging
from src.processing.pdf_processor import process_pdfs_to_documents

# --- Setup Logging --- 
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

MAX_FILES = 3
MAX_FILE_SIZE_MB = 50
ALLOWED_MIME_TYPES = ['application/pdf']
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Load environment variables from .env file
load_dotenv()

# --- Check for necessary environment variables ---
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
if not LANGCHAIN_API_KEY:
    st.error("Error: LANGCHAIN_API_KEY environment variable not set.")
    st.stop() # Stop execution if the key is missing

# --- Session State Initialization ---
if 'faiss_index' not in st.session_state:
    st.session_state.faiss_index = None
    logger.debug("Initialized 'faiss_index' in session state to None.")
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []
    logger.debug("Initialized 'processed_docs' in session state to empty list.")
if 'uploaded_file_names' not in st.session_state:
    st.session_state.uploaded_file_names = [] # Store names to detect changes
    logger.debug("Initialized 'uploaded_file_names' in session state to empty list.")

# --- Helper Functions ---
def validate_uploaded_files(uploaded_files_list):
    """
    Validates a list of uploaded files based on type and size constraints.

    Args:
        uploaded_files_list: A list of Streamlit UploadedFile objects.

    Returns:
        A tuple containing:
            - valid_files (list): A list of valid UploadedFile objects.
            - error_messages (list): A list of strings describing validation errors.
    """
    valid_files = []
    error_messages = []
    for file in uploaded_files_list:
        is_valid = True
        # Validate type
        if file.type not in ALLOWED_MIME_TYPES:
            error_messages.append(f"'{file.name}': Invalid file type ({file.type}). Only PDF files are allowed.")
            is_valid = False

        # Validate size
        if file.size > MAX_FILE_SIZE_BYTES:
            error_messages.append(f"'{file.name}': File size ({file.size / 1024 / 1024:.1f} MB) exceeds the {MAX_FILE_SIZE_MB} MB limit.")
            is_valid = False

        if is_valid:
            valid_files.append(file)
    return valid_files, error_messages

# --- UI Layout --- 
st.title("PDF RAG Chat")

# --- File Upload Section ---
uploaded_files = st.file_uploader(
    "Upload your PDF documents (max 3 files, 50MB each)",
    accept_multiple_files=True
)

files_changed = False
if uploaded_files:
    if len(uploaded_files) > MAX_FILES:
        st.error(f"Error: You can only upload a maximum of {MAX_FILES} files at a time.")
        # Clear relevant session state on error
        st.session_state.uploaded_file_names = []
        st.session_state.faiss_index = None
        st.session_state.processed_docs = []
    else:
        # Validate uploaded files
        valid_files, error_messages = validate_uploaded_files(uploaded_files)

        # Display errors if any
        if error_messages:
            for error in error_messages:
                st.error(error)
            # Clear state if errors occurred
            st.session_state.uploaded_file_names = []
            st.session_state.faiss_index = None
            st.session_state.processed_docs = []
        
        # Check if the set of valid files has changed
        current_file_names = sorted([f.name for f in valid_files])
        if current_file_names != st.session_state.get('uploaded_file_names', []):
            files_changed = True
            st.session_state.uploaded_file_names = current_file_names
            logger.info(f"Detected change in uploaded files: {current_file_names}")
            # Reset index and docs when files change
            st.session_state.faiss_index = None
            st.session_state.processed_docs = []

        # Display success/warning for valid files 
        if valid_files:
            if not error_messages: # Only show success if no errors for any file
                st.success(f"Successfully validated {len(valid_files)} PDF file(s): {', '.join(current_file_names)}")
        elif not error_messages: # Handle case where <= MAX_FILES are uploaded, but none are valid
             st.warning("No valid PDF files were uploaded. Please ensure files are PDFs and under 50MB.")
             st.session_state.uploaded_file_names = [] # Clear state here too
             st.session_state.faiss_index = None
             st.session_state.processed_docs = []
             
        # --- Index Building Logic (if valid files exist and changed or index missing) ---
        if valid_files and (files_changed or st.session_state.faiss_index is None):
            logger.info("Valid files uploaded or changed, proceeding to process and build index...")
            with st.spinner("Processing PDFs and building vector index..."):
                try:
                    # Pass the list of valid UploadedFile objects
                    processed_docs = process_pdfs_to_documents(valid_files)
                    if processed_docs:
                        st.session_state.processed_docs = processed_docs
                        logger.info(f"Successfully processed {len(processed_docs)} documents from {len(valid_files)} files.")
                        
                        # Build the FAISS index in memory
                        st.session_state.faiss_index = build_faiss_index(processed_docs)
                        
                        if st.session_state.faiss_index:
                            logger.info("FAISS index built and stored in session state successfully.")
                            st.success("Vector index ready.")
                        else:
                            logger.error("Failed to build FAISS index after processing documents.")
                            st.error("Failed to build the vector index from the documents.")
                    else:
                        logger.warning("PDF processing returned no documents.")
                        st.warning("Could not extract text from the provided PDF(s). Index not built.")
                        st.session_state.faiss_index = None # Ensure index is None
                        st.session_state.processed_docs = []

                except Exception as e:
                    logger.exception("An error occurred during PDF processing or index building.")
                    st.error(f"An error occurred during PDF processing: {e}")
                    st.session_state.faiss_index = None # Ensure index is None on error
                    st.session_state.processed_docs = []

elif not uploaded_files and st.session_state.get('uploaded_file_names', []):
    # If files are removed via the UI, clear the state
    logger.info("Files removed from uploader. Clearing index and docs from session state.")
    st.session_state.uploaded_file_names = []
    st.session_state.faiss_index = None
    st.session_state.processed_docs = []
    st.info("PDFs removed. Upload new files to chat.") # Inform user

# --- Display Current State --- 
st.divider()
if st.session_state.get('faiss_index'):
    st.subheader(f"Index Ready for {len(st.session_state.get('uploaded_file_names',[]))} PDFs")
    st.caption(f"({len(st.session_state.get('processed_docs',[]))} document chunks indexed)")
else:
    st.caption("No vector index ready. Upload valid PDF files.")

st.divider()

# --- Query Input and Processing ---
user_query = st.text_input("Ask a question about your documents:", key="query_input")

if user_query:
    # Check if index is ready in session state
    if st.session_state.get('faiss_index') is None:
        logger.warning("Query attempt failed: FAISS index not found in session state.")
        st.warning("Please upload valid PDF documents and wait for processing before asking a question.")
    else:
        logger.info(f"Processing query: '{user_query[:50]}...' using in-memory index.")
        try:
            # Retrieve index from session state
            index = st.session_state.faiss_index
            
            logger.debug("Calling query processor...")
            # Note: process_query might not be needed if it only formats text.
            # If the RAG chain handles formatting, you could pass user_query directly.
            formatted_query_or_original = process_query(user_query) # Assuming this returns the string to search with
            logger.debug(f"Query for search: {formatted_query_or_original}")

            st.divider()
            logger.info("Attempting document retrieval from session state index...")
            try:
                # Use the index directly from session state
                results = search_index(formatted_query_or_original, index, top_k=3)
                
                if results:
                    logger.info(f"Retrieved {len(results)} relevant chunks from in-memory index.")
                    st.success(f"Retrieved {len(results)} relevant chunks:")
                    # Display retrieved chunks (optional but good for debugging)
                    with st.expander("Show Retrieved Chunks"):
                        for i, doc in enumerate(results):
                            source = doc.metadata.get('source', 'N/A')
                            page = doc.metadata.get('page', 'N/A')
                            logger.debug(f"Retrieved chunk {i+1}: Source: {source}, Page: {page}, Content: {doc.page_content[:100]}...")
                            st.info(f"**Chunk {i+1} (Source: {source}, Page: {page})**\n{doc.page_content[:300]}...")
                    
                    # --- Answer Generation --- 
                    if LANGCHAIN_API_KEY:
                        st.divider()
                        logger.info("Generating answer using retrieved chunks...")
                        with st.spinner("Generating answer..."):
                             # Create retriever from the session state index
                            retriever = index.as_retriever(search_kwargs={"k": 3})
                            try:
                                final_answer = generate_answer(user_query, retriever)
                                logger.info("Answer generated successfully.")
                                st.subheader("Generated Answer:")
                                st.write(final_answer)
                            except Exception as e:
                                logger.exception("An error occurred during answer generation.")
                                st.error("An error occurred while generating the answer.")
                    else:
                        logger.error("Cannot generate answer: LangChain API Key is missing.")
                        st.error("Cannot generate answer: LangChain API Key is missing.")

                else:
                    logger.warning("Retrieval from in-memory index found no relevant chunks.")
                    st.warning("Could not find relevant information in the documents for your query.")
            
            except Exception as e:
                logger.exception("An error occurred during search_index or subsequent processing.")
                st.error(f"An error occurred during document retrieval or processing: {e}")

        except ValueError as e:
            logger.error(f"Error processing query input: {e}")
            st.error(f"Error processing query input: {e}")
        except Exception as e:
            logger.exception("An unexpected error occurred during query handling.")
            st.error(f"An unexpected error occurred: {e}") 
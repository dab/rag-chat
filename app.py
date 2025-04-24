import streamlit as st
import logging
import sys
from src.processing.query_processor import process_query, logger
from src.retrieval.vector_store import load_faiss_index, search_index, DEFAULT_FAISS_INDEX_PATH
from src.generation.answer_generator import generate_answer

MAX_FILES = 3
MAX_FILE_SIZE_MB = 50
ALLOWED_MIME_TYPES = ['application/pdf']
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

st.title("RAG Chat")

uploaded_files = st.file_uploader(
    "Upload your PDF documents (max 3 files, 50MB each)",
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > MAX_FILES:
        st.error(f"Error: You can only upload a maximum of {MAX_FILES} files at a time.")
        st.session_state['valid_pdf_files'] = [] # Clear session state on this error
    else:
        valid_files = []
        error_messages = []
        for file in uploaded_files:
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

        # Display errors first
        if error_messages:
            for error in error_messages:
                st.error(error)

        # Display success message for valid files
        if valid_files:
            st.success(f"Successfully validated {len(valid_files)} PDF file(s):")
            for valid_file in valid_files:
                st.write(valid_file.name)
            st.session_state['valid_pdf_files'] = valid_files # Store valid files in session state
        elif not error_messages: # Handle case where <= MAX_FILES are uploaded, but none are valid PDFs/correct size
             st.warning("No valid PDF files were uploaded. Please ensure files are PDFs and under 50MB.")
             st.session_state['valid_pdf_files'] = [] # Clear session state here too

# Display currently stored valid PDFs from session state
st.divider()
if 'valid_pdf_files' in st.session_state and st.session_state['valid_pdf_files']:
    st.subheader("Session State: Valid PDFs Ready for Processing")
    for stored_file in st.session_state['valid_pdf_files']:
        st.write(f"- {stored_file.name} ({stored_file.size / 1024 / 1024:.1f} MB)")
else:
    st.caption("Session State: No valid PDF files currently stored.")

st.divider()

# --- Query Input and Processing ---
user_query = st.text_input("Ask a question about your documents:")

if user_query:
    if 'valid_pdf_files' in st.session_state and st.session_state['valid_pdf_files']:
        try:
            # Setup basic logging if not already configured
            # Ensure logger is configured before first use
            if not logging.getLogger().hasHandlers():
                 logging.basicConfig(stream=sys.stdout, level=logging.INFO)

            st.write("Processing query...")
            formatted_output = process_query(user_query)
            st.success(f"LangChain Formatted Output:")
            st.code(formatted_output, language=None) # Use st.code for better formatting
            # TODO: Add logic to use processed_query for retrieval and generation

            st.divider()
            st.write("Attempting retrieval...")
            try:
                loaded_index = load_faiss_index(DEFAULT_FAISS_INDEX_PATH)
                if loaded_index:
                    # Using the formatted_output might not be ideal long term, but using it for now
                    # Consider using the original `processed_query` before formatting for semantic search.
                    results = search_index(formatted_output, loaded_index, top_k=3) 
                    if results:
                        st.success(f"Retrieved {len(results)} relevant chunks:")
                        for i, doc in enumerate(results):
                            # Display basic info, assuming metadata might be useful later
                            st.info(f"Chunk {i+1}:\n{doc.page_content[:500]}...\n(Source: {doc.metadata.get('source', 'N/A')}, Page: {doc.metadata.get('page', 'N/A')})") # Added metadata display

                        # --- Generate Answer --- 
                        st.divider()
                        st.write("Generating answer based on retrieved context...")
                        # We need the retriever object itself, not just the results
                        # Assuming load_faiss_index returns the retriever compatible with LangChain
                        retriever = loaded_index.as_retriever(search_kwargs={"k": 3})
                        # Use the *original* user_query for answer generation
                        try:
                            final_answer = generate_answer(user_query, retriever)
                            st.subheader("Generated Answer:")
                            st.write(final_answer)
                        except Exception as e:
                            logger.exception(f"An error occurred during answer generation: {e}")
                            st.error("An error occurred while generating the answer.")
                        # --- End Generate Answer ---

                    else:
                        st.warning("Retrieval succeeded but found no relevant chunks for the formatted query.")
                else:
                    st.error("FAISS index not found or could not be loaded. "
                             "Please ensure documents are uploaded and processed to create the index.")
            except Exception as e:
                logger.exception(f"An error occurred during retrieval: {e}")
                st.error("An error occurred during document retrieval.")

        except ValueError as e:
            logger.error(f"Error processing query: {e}")
            st.error(f"Error: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred during query processing: {e}")
            st.error("An unexpected error occurred. Please try again.")
    else:
        st.warning("Please upload valid PDF documents before asking a question.") 
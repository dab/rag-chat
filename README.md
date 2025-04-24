# PDF RAG Chat 📄💬

Chat with your PDF documents! This simple web application allows you to upload up to three PDF files and ask questions about their content using the power of Retrieval-Augmented Generation (RAG).

It's designed to help researchers, professionals, and developers quickly find information within lengthy documents without manual searching. This is currently an MVP (Minimum Viable Product) focused on core functionality.

## ✨ Features

*   ⬆️ **Multi-PDF Upload:** Upload up to 3 text-based PDF files simultaneously.
*   📄 **File Limits:** Each PDF must be less than 50MB.
*   💬 **Interactive Chat:** Ask questions in a simple chat interface and get answers based *only* on the content of your uploaded documents.
*   🧠 **RAG Powered:** Uses LangChain and FAISS to retrieve relevant text chunks and generate accurate answers.
*   🔗 **Source Attribution:** Answers include references to the specific parts of the source PDFs they were derived from.
*   💨 **Temporary Sessions:** Uploaded files and extracted data are stored in memory and are cleared when you close the app or upload new files. No data persists.

## 🚀 Technologies Used

*   🐍 Python 3.10+
*   🎈 Streamlit (Web UI Framework)
*   🔗 LangChain (RAG Orchestration & Core Logic)
*   💾 FAISS (CPU) (Fast Vector Similarity Search)
*   📄 PyPDF2 (PDF Text Extraction)
*   🧪 Pytest (Unit Testing Framework)
*   🔑 OpenAI (LLM for generating answers - **Requires API Key**)
*   🤗 HuggingFace Sentence Transformers (Embeddings Model: `all-MiniLM-L6-v2`)

## 🔧 Setup & Installation

Follow these steps to get the application running locally.

**Prerequisites:**

*   Python 3.10 or later installed.
*   `pip` (Python package installer, usually comes with Python).
*   An **OpenAI API Key**. Get one from [OpenAI Platform](https://platform.openai.com/api-keys).

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url> # Replace with the actual URL
    cd pdf-rag-chat
    ```

2.  **Create and activate a virtual environment:**
    *   On Linux/macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   The application uses environment variables for configuration, especially API keys.
    *   Copy the example file:
        ```bash
        cp .env.example .env
        ```
        *(If `.env.example` doesn't exist, create it manually based on the content below).*
    *   Open the `.env` file in your text editor and add your **OpenAI API Key**.
        ```dotenv
        # --- .env / .env.example ---

        # REQUIRED: Your OpenAI API Key for the language model
        OPENAI_API_KEY="sk-..."

        # Optional: Set to "true" to enable LangSmith tracing (requires LANGCHAIN_API_KEY)
        # LANGCHAIN_TRACING_V2="false"
        # LANGCHAIN_API_KEY="ls_..."

        # Optional: Logging configuration
        LOG_LEVEL="INFO" # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        LOG_FILE_PATH="./logs/app.log" # Path where the log file will be saved
        ```
    *   **🔒 Security Note:** The `.env` file is listed in `.gitignore`. **Never** commit this file to version control, as it contains sensitive credentials.

## ▶️ How to Run

1.  Make sure your virtual environment is activated.
2.  Navigate to the project's root directory (`pdf-rag-chat/`).
3.  Run the Streamlit application:
    ```bash
    streamlit run src/app.py
    ```
4.  Streamlit will provide a local URL (usually `http://localhost:8501`). Open this URL in your web browser.

## 📂 Project Structure

```
pdf-rag-chat/
├── .env              # Local environment variables (KEEP SECRET!)
├── .env.example      # Example environment variables template
├── .gitignore        # Specifies intentionally untracked files that Git should ignore
├── requirements.txt  # Python package dependencies
├── README.md         # This file: project documentation
├── src/              # Main source code directory
│   ├── __init__.py
│   ├── app.py            # Main Streamlit application script (entry point)
│   ├── config.py         # Handles loading configuration (env vars, logging setup)
│   ├── processing/       # Modules for data processing
│   │   ├── __init__.py
│   │   ├── pdf_processor.py  # Logic for loading, validating, and chunking PDFs
│   │   └── query_processor.py # Logic for handling and formatting user queries
│   ├── retrieval/        # Modules for information retrieval
│   │   ├── __init__.py
│   │   └── vector_store.py   # Manages embeddings and FAISS vector store operations
│   ├── generation/       # Modules for answer generation
│   │   ├── __init__.py
│   │   └── answer_generator.py # Constructs and runs the RAG chain, formats output
│   └── ui/               # (Optional structure) Contains Streamlit UI helper functions
│       └── __init__.py
├── tests/            # Contains all tests
│   ├── __init__.py
│   ├── test_pdf_processor.py # Example test file for pdf_processor
│   └── ...             # Other unit and integration test files
└── logs/             # Directory for log files (created automatically if logging to file)
    └── app.log         # Default log file
```

## 🧪 Testing

*   Unit tests are written using the `pytest` framework.
*   To run all tests, navigate to the project root and run:
    ```bash
    pytest
    ```
*   The project aims for a unit test code coverage of ≥80%.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or find bugs, please open an issue or submit a pull request. (Further details can be added later if needed).

## 📜 License

This project is licensed under the MIT License.

## 🔗 Useful Links

*   [Product Requirements Document](./.ai/prd.md)
*   [Architecture Document](./.ai/arch.md)
*   [LangChain Documentation](https://python.langchain.com/)
*   [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
*   [Streamlit Documentation](https://docs.streamlit.io/)
*   [OpenAI Platform](https://platform.openai.com/) 
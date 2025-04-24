# PDF RAG Chat

This application allows you to chat with your PDF documents using Retrieval-Augmented Generation (RAG).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd pdf-rag-chat
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    *   This application requires certain configuration values, such as API keys, to be set as environment variables.
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
        *(Note: If `.env.example` does not exist, please create it manually with the required variables like `LANGCHAIN_API_KEY="YOUR_KEY_HERE"`)*
    *   Open the `.env` file and replace the placeholder values with your actual credentials.
    *   The following variables are currently used:
        *   `LANGCHAIN_API_KEY`: Your API key for LangChain services.
        *   `LOG_LEVEL`: The minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
        *   `LOG_FILE_PATH`: The path for the log file. Defaults to `./logs/app.log`.
    *   **Important:** The `.env` file is included in `.gitignore` and should **never** be committed to version control.

## Running the Application

```bash
streamlit run app.py
```

## Running Tests

```bash
pytest
``` 
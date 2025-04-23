
# Backlog of Epics and User Stories

## Epic 1: Project Setup
**Goal:** Establish the foundational development environment and initial application structure to enable feature development.

- **Story 1: Set up project structure and dependencies**  
  As a developer, I want to create the project directory, set up a Python 3.10 virtual environment, install required dependencies (Streamlit, LangChain, FAISS, PyPDF2, Pytest, Selenium), initialize the Streamlit app with a basic title, and set up the testing directory so that I can start building the application.

## Epic 2: PDF Upload and Validation
**Goal:** Enable users to upload and validate PDFs, ensuring only valid files are processed.

- **Story 2: Add PDF file uploader to the UI**  
  As a user, I want to upload up to three PDFs through the application so that I can ask questions about their content.
- **Story 3: Validate uploaded PDFs**  
  As a user, I want the application to ensure that uploaded files are PDFs, each less than 50 MB, and no more than three files, so that only valid files are processed.
- **Story 4: Store uploaded PDFs temporarily**  
  As a developer, I want to store the uploaded PDFs in memory or a temporary directory so that they can be accessed for text extraction.
- **Story 5: Display error messages for invalid uploads**  
  As a user, I want to see clear error messages (e.g., "Only PDFs allowed. Please try again.") if my upload fails due to invalid file type, size, or count, so that I can correct the issue.

## Epic 3: PDF Processing and Indexing
**Goal:** Process uploaded PDFs into a searchable format to support answer generation.

- **Story 6: Extract text from uploaded PDFs**  
  As a developer, I want to extract text from the uploaded PDFs using PyPDF2 or a similar library so that the text can be indexed for search.
- **Story 7: Chunk extracted text for indexing**  
  As a developer, I want to split the extracted text into smaller chunks so that they can be efficiently indexed and retrieved.
- **Story 8: Create FAISS index for text chunks**  
  As a developer, I want to create a FAISS index of the text chunks so that relevant chunks can be quickly retrieved for answer generation.

## Epic 4: Answer Generation
**Goal:** Allow users to ask questions and receive accurate answers based on the uploaded PDFs.

- **Story 9: Add query input field to the UI**  
  As a user, I want to enter questions about the uploaded PDFs so that I can receive answers.
- **Story 10: Process user queries with LangChain**  
  As a developer, I want to use LangChain to process the user’s query and prepare it for retrieval so that relevant information can be identified.
- **Story 11: Retrieve relevant chunks using FAISS**  
  As a developer, I want to retrieve the most relevant text chunks from the FAISS index based on the user’s query so that accurate answers can be generated.
- **Story 12: Generate answers using RAG pipeline**  
  As a developer, I want to use the RAG pipeline to generate answers based on the retrieved chunks and the user’s query so that users receive meaningful responses.
- **Story 13: Display answers and source attributions**  
  As a user, I want to see the generated answer along with the source PDF name and page number (e.g., "Source: [PDF_Name], Page [X]") so that I can verify the information.
- **Story 14: Handle errors in answer generation**  
  As a user, I want to see a friendly message (e.g., "Sorry, we couldn’t generate an answer. Please try again.") if the application cannot generate an answer, so that I know to try again or adjust my query.

## Epic 5: Testing
**Goal:** Ensure the application is reliable, functional, and meets performance and usability requirements.

- **Story 15: Write unit tests for PDF validation logic**  
  As a developer, I want to write Pytest unit tests to ensure the PDF validation logic correctly handles edge cases (e.g., invalid file types, oversized files, exceeding the file count limit) so that the upload feature is robust.
- **Story 16: Write unit tests for answer generation logic**  
  As a developer, I want to write Pytest unit tests to verify the accuracy and reliability of the answer generation logic using mock data so that the core functionality is dependable.
- **Story 17: Conduct end-to-end testing with Selenium**  
  As a developer, I want to perform end-to-end tests using Selenium to simulate user interactions (uploading three PDFs and asking five questions, including edge cases like empty or large PDFs) so that the entire system meets performance (<5s answer time) and usability standards.

## Epic 6: Deployment
**Goal:** Make the application accessible to users in a production environment.

- **Story 18: Deploy the application to Render**  
  As a developer, I want to deploy the application to Render’s free tier, ensuring it is accessible via HTTPS and functions correctly with a test query, so that users can access and use it.

# Product Requirements Document (PRD): PDF RAG Chat MVP

## Purpose
Build a simple chat app that allows users to upload up to three PDFs (each <50 MB) and ask questions about their content, with answers generated using Retrieval-Augmented Generation (RAG).

## Context
This MVP targets users needing quick insights from PDFs without manual searching. It prioritizes simplicity, speed, and usability over advanced features.

## Story (Task) List

### Epic 1: PDF Upload
**Story 3: Implement PDF Upload Functionality**  
- Create a Streamlit file uploader for PDFs.  
- Validate file type (PDF only) and size (<50 MB each).  
- Enforce a limit of three PDFs per upload.  
- Store PDFs temporarily in memory or a session directory.  
- Display simple error notifications for invalid uploads (e.g., "Only PDFs allowed. Please try again.").  
- Log detailed error information in the console and logger for debugging.  

### Epic 2: Answer Generation
**Story 5: Develop Answer Generation Logic**  
- Build a query processing function using LangChain.  
- Use FAISS to retrieve top relevant document chunks.  
- Generate answers with LangChain’s RAG pipeline.  
- Handle exceptions during answer generation and display a user-friendly message (e.g., "Sorry, we couldn't generate an answer. Please try again.").  
- Log exception details for debugging.  
- Validate answer relevance with test questions.  

**Story 6: Implement Source Attribution**  
- Display relevant PDF excerpts alongside answers.  
- Format as "Source: [PDF_Name], Page [X]".  

### Epic 3: Testing
**Story 9: Write Unit Tests**  
- Write Pytest cases for PDF validation logic, including edge cases like empty PDFs and malformed files.  
- Test answer generation with mock PDF data.  
- Achieve 80%+ code coverage.  

**Story 11: Perform End-to-End Testing**  
- Simulate uploading three PDFs and asking five questions.  
- Include edge case PDFs such as empty files and large PDFs.  
- Use Selenium to automate browser testing.  
- Confirm performance (<5s answer time) and usability.  

### Epic 5: Deployment
**Story 13: Deploy to Render**  
- Deploy the app to Render using the free tier.  
- Ensure the app is accessible via HTTPS.  
- Verify deployment with a test query.  

## Testing Strategy
- **Unit Tests**: Pytest for backend components (e.g., PDF validation, RAG logic).  
  - Include tests for edge cases such as empty PDFs, malformed PDFs, and PDFs with no text.  
- **Integration Tests**: Mock frontend-backend calls to ensure data flow.  
- **End-to-End (e2e) Tests**: Selenium for full user scenarios (upload, query, answer).  
  - Test with multiple PDFs of varying sizes, including large PDFs up to 50 MB.  
  - Verify performance and usability with edge case PDFs.  

## UX/UI
- Streamlit frontend with a file uploader, text input for questions, and a chat-style output for answers and sources.

## Tech Stack
| Component          | Technology       | Version |
|--------------------|------------------|---------|
| Language           | Python           | 3.10    |
| Frontend           | Streamlit        | Latest  |
| Backend            | LangChain, FAISS | Latest  |
| Deployment         | Render           | N/A     |
| Testing            | Pytest, Selenium | Latest  |

## Out of Scope Post MVP
- User authentication.
- Persistent storage of PDFs.
- Advanced query parsing (e.g., multi-intent questions).

## High-Level Architecture
- **Frontend**: Streamlit for UI and user interaction.  
- **Backend**: LangChain for RAG, FAISS for vector search.  
- **Deployment**: Render with HTTPS.

## Project Directory Tree
```
pdf_rag_chat/
├── app.py              # Streamlit app
├── rag_logic.py        # RAG pipeline
├── pdf_processor.py    # PDF handling
├── tests/              # Unit and e2e tests
│   ├── test_pdf.py
│   └── test_e2e.py
└── README.md
```

## Unknowns, Assumptions, and Risks
- **Assumption**: PDFs are text-extractable (not scanned images).  
- **Risk**: Performance may degrade with complex PDFs; mitigated by size limits and testing.  
- **Unknown**: Optimal FAISS index size for <50 MB PDFs; to be tuned during development.

## Non-Functional Requirements
- **Performance**: Answer generation within 5 seconds for standard PDFs (<50 MB each, up to 3 PDFs).  
- **Security**: Basic HTTPS via Render deployment.

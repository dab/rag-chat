# Story 2.5: Source Attribution

## Story

**As a** user
**I want** to see source attributions formatted as "Source: [PDF_Name], Page [X]" alongside each answer
**so that** I can verify the information and understand its origin.

## Status

Complete

## Context

Currently, the RAG pipeline generates answers based on retrieved document chunks, but it doesn't explicitly return which source documents (and pages) were used. This story involves modifying the RAG chain or the surrounding logic to retain and return source information (PDF filename and page number) associated with the context used for generating the answer. The final output presented to the user should include both the answer and these formatted sources.

## Estimation

Story Points: 2

## Acceptance Criteria

1. - [ ] The RAG pipeline identifies the source documents and page numbers used to generate the answer.
2. - [ ] The function/API endpoint responsible for generating answers returns both the answer string and a list of source attributions.
3. - [ ] Each source attribution includes the original PDF filename and the relevant page number.
4. - [ ] The final output presented (e.g., returned by the API) includes the generated answer followed by formatted source strings like "Source: [PDF_Name], Page [X]".
5. - [ ] If multiple sources contribute, all relevant sources are listed.
6. - [ ] If no specific source can be attributed (e.g., answer generated from general knowledge or multiple combined snippets without clear origin mapping), no source is listed or a generic message is provided.

## Subtasks

1. - [x] Investigate LangChain RAG chain capabilities for returning source documents (e.g., checking if the retriever's results or intermediate steps are accessible).
2. - [x] Modify the `create_rag_chain` function in `src/generation/answer_generator.py` (or related components) to pass through or return the source document metadata alongside the answer.
3. - [x] Update the `generate_answer` function in `src/generation/answer_generator.py` to handle the output containing both the answer and source metadata.
4. - [x] Extract PDF filename and page number from the source document metadata. (Requires knowing the metadata structure).
5. - [x] Format the source information into the string "Source: [PDF_Name], Page [X]".
6. - [x] Structure the return value of `generate_answer` to include both the answer string and a list of formatted source strings (or a combined string).
7. - [x] Add/Update unit tests in `tests/test_answer_generator.py` to verify that source information is correctly extracted, formatted, and returned alongside the answer.

## Testing Requirements:**

    - Unit tests should cover the logic for extracting and formatting source information.
    - Mocks should include documents with expected metadata (filename, page number).
    - Tests should verify the structure of the return value from `generate_answer`.
    - Code coverage >= 85%.

## Story Wrap Up (To be filled in AFTER agent execution):**

- **Agent Model Used:** `Gemini 2.5 Pro`
- **Agent Credit or Cost:** `N/A`
- **Date/Time Completed:** `Thu Apr 24 13:20:06 EEST 2025`
- **Commit Hash:** `77373490237f2e9329c0e44db4e6e3a4be656605`
- **Change Log**
  - Refactored `create_rag_chain` in `src/generation/answer_generator.py` to return source documents (`context`) alongside the answer using LCEL `RunnableParallel` and `assign`.
  - Modified `generate_answer` in `src/generation/answer_generator.py` to process the dictionary output, extract source metadata (filename, page), format it, and return `{"answer": ..., "sources": ...}`.
  - Updated `tests/test_answer_generator.py`: Added metadata to mock documents, adjusted mocks for chain output, and updated assertions to verify the new return structure and source formatting.
    ... 
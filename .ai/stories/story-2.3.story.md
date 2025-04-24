# Story 2.3: Implement RAG Answer Generation

## Story

**As a** developer
**I want** to generate answers with LangChain's RAG pipeline
**so that** users receive accurate responses based on the PDFs.

## Status

In-Progress

## Context

{With query processing (Story 2.1) and document retrieval (Story 2.2) in place, this story focuses on connecting these components and using a Large Language Model (LLM) via LangChain to generate a final answer based on the retrieved context.}

## Estimation

Story Points: {Story Points}

## Acceptance Criteria

1.  - [x] Necessary LangChain components for RAG (e.g., LLM wrappers, `RunnablePassthrough`, `StrOutputParser`, prompt templates) are available/imported.
2.  - [x] An LLM is configured (e.g., using `ChatOpenAI` or another provider via `langchain-community`). Requires necessary API keys/setup.
3.  - [x] A LangChain Expression Language (LCEL) chain is constructed that:
    1.  - [x] Takes the original query and retrieved documents as input.
    2.  - [x] Formats a prompt including the context (retrieved docs) and the question.
    3.  - [x] Invokes the LLM with the formatted prompt.
    4.  - [x] Parses the LLM output into a string answer.
4.  - [x] The RAG chain is integrated into `app.py`, replacing the placeholder retrieval display.
5.  - [x] The generated answer is displayed to the user in the Streamlit app.
6.  - [x] Basic error handling for the RAG chain execution is implemented.
7.  - [x] Unit tests are written for the RAG chain logic (mocking LLM calls and retrieval).

## Subtasks

1.  - [x] Add LLM provider dependencies (e.g., `langchain-openai`) to `requirements.txt`.
2.  - [x] Configure LLM access (e.g., environment variables for API keys like `OPENAI_API_KEY`). Add `.env` to `.gitignore` if not already present. (User confirmed `.env` creation)
3.  - [x] Create a new module `src/generation/answer_generator.py`.
4.  - [x] Implement a function `create_rag_chain(retriever, llm)` that defines the LCEL chain (prompt formatting, LLM call, output parsing).
    1.  - [x] Define a suitable prompt template (e.g., `ChatPromptTemplate`) that incorporates context and question.
    2.  - [x] Initialize the chosen LLM (e.g., `ChatOpenAI`).
    3.  - [x] Construct the chain using `RunnablePassthrough`, the prompt, the LLM, and `StrOutputParser` (Refactored to use `RunnableLambda`).
5.  - [x] Implement a function `generate_answer(query: str, retriever)` that uses the created chain.
6.  - [x] Integrate `generate_answer` into `app.py`, calling it after successful retrieval and displaying the result.
7.  - [x] Add error handling for chain invocation.
8.  - [x] Write unit tests for `answer_generator.py`, mocking the retriever and LLM components.

## Testing Requirements:**

- Reiterate the required code coverage percentage (e.g., >= 85%).

## Story Wrap Up (To be filled in AFTER agent execution):**

- **Agent Model Used:** `<Agent Model Name/Version>`
- **Agent Credit or Cost:** `<Cost/Credits Consumed>`
- **Date/Time Completed:** `<Timestamp>`
- **Commit Hash:** `<Git Commit Hash of resulting code>`
- **Change Log**
  - ... 
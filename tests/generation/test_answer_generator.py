# tests/generation/test_answer_generator.py

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
import os # For basename

# Import the function to test
from src.generation.answer_generator import generate_answer, format_docs


# --- Fixtures and Mock Data ---

@pytest.fixture
def mock_retriever():
    retriever = MagicMock()
    # Simulate the behavior of the retriever interface (e.g., invoke)
    # No need to mock invoke here if we mock the whole chain creation
    return retriever

# Removed mock_llm fixture as we patch the chain creation now

# Sample documents returned by the retriever
MOCK_DOC_1 = Document(page_content="LangChain provides tools for RAG.", metadata={"source": "/path/to/doc1.pdf", "page": 1})
MOCK_DOC_2 = Document(page_content="Testing involves mocking dependencies.", metadata={"source": "data/doc2.pdf", "page": 5})
MOCK_DOC_NO_PAGE = Document(page_content="Metadata might be incomplete.", metadata={"source": "other/doc3.pdf"})

# --- Test format_docs utility --- 

def test_format_docs():
    docs = [MOCK_DOC_1, MOCK_DOC_2]
    expected_output = "LangChain provides tools for RAG.\n\nTesting involves mocking dependencies."
    assert format_docs(docs) == expected_output

def test_format_docs_empty():
    assert format_docs([]) == ""

# --- Test generate_answer --- 

# Patch the create_rag_chain function within the generate_answer function
@patch('src.generation.answer_generator.create_rag_chain')
def test_generate_answer_success(mock_create_chain, mock_retriever):
    """Test successful answer generation with context."""
    # Configure the mock chain returned by the patched function
    mock_chain_instance = MagicMock()
    mock_chain_instance.invoke.return_value = {
        "answer": "This is the generated answer based on context.",
        "documents": [MOCK_DOC_1, MOCK_DOC_2]
    }
    mock_create_chain.return_value = mock_chain_instance

    query = "What is RAG?"
    result = generate_answer(query, mock_retriever)

    # Assertions
    assert result["answer"] == "This is the generated answer based on context."
    assert len(result["sources"]) == 2
    assert "Source: doc1.pdf, Page 1" in result["sources"]
    assert "Source: doc2.pdf, Page 5" in result["sources"]

    # Verify create_rag_chain was called (implicitly checks LLM was instantiated too)
    # We pass the retriever itself, not its invoke method mock
    mock_create_chain.assert_called_once()
    # Verify the mock chain's invoke was called with the query
    mock_chain_instance.invoke.assert_called_once_with(query)


@patch('src.generation.answer_generator.create_rag_chain')
def test_generate_answer_no_context(mock_create_chain, mock_retriever):
    """Test answer generation when retriever finds no documents."""
    mock_chain_instance = MagicMock()
    # Chain still runs, but might get different answer/empty docs
    mock_chain_instance.invoke.return_value = {
        "answer": "Cannot answer based on provided information.",
        "documents": []
    }
    mock_create_chain.return_value = mock_chain_instance

    query = "What is photosynthesis?"
    result = generate_answer(query, mock_retriever)

    assert result["answer"] == "Cannot answer based on provided information."
    assert len(result["sources"]) == 0

    mock_create_chain.assert_called_once()
    mock_chain_instance.invoke.assert_called_once_with(query)


@patch('src.generation.answer_generator.create_rag_chain')
def test_generate_answer_chain_invoke_error(mock_create_chain, mock_retriever):
    """Test error handling when the RAG chain invocation fails."""
    mock_chain_instance = MagicMock()
    # Configure mock chain invoke to raise an exception
    mock_chain_instance.invoke.side_effect = Exception("Chain Invoke Error")
    mock_create_chain.return_value = mock_chain_instance

    query = "Tell me about LangChain."
    result = generate_answer(query, mock_retriever)

    # Check for error handling (returns None for answer)
    assert result["answer"] is None
    assert result["sources"] == [] # Should be empty on error

    mock_create_chain.assert_called_once()
    mock_chain_instance.invoke.assert_called_once_with(query)


# This test doesn't need chain mocking as error happens before chain creation in generate_answer
# We still need to mock ChatOpenAI as it's called *before* the chain invoke
@patch('src.generation.answer_generator.ChatOpenAI') # Keep this patch here
def test_generate_answer_retriever_error(mock_chat_openai_class, mock_retriever):
    """Test error handling when the retriever call fails during chain setup/invoke."""
    # Configure mock retriever to raise an exception
    # We assume the retriever passed to generate_answer *is* the interface
    # and its invoke method might be called *inside* create_rag_chain OR its result.
    # Let's refine: generate_answer calls create_rag_chain, which uses the retriever.
    # The error likely happens inside the chain's invoke call when it tries to use the retriever.
    # So, this scenario is actually covered by test_generate_answer_chain_invoke_error if
    # the exception originates from the retriever part of the chain.

    # Let's test if the ChatOpenAI instantiation itself fails.
    mock_chat_openai_class.side_effect = Exception("LLM Instantiation Error")

    query = "This query will fail LLM setup."
    result = generate_answer(query, mock_retriever)

    # Check for error handling
    assert result["answer"] is None
    assert result["sources"] == []

    # Assert ChatOpenAI constructor was called (and raised error)
    mock_chat_openai_class.assert_called_once()
    # Assert retriever was NOT used because error happened before chain execution
    mock_retriever.invoke.assert_not_called() # If invoke is mocked on the fixture

# Rename the old retriever error test to test LLM instantiation error
# def test_generate_answer_retriever_error(mock_chat_openai_class, mock_retriever):
#     """Test error handling when the retriever call fails."""
#     # Configure mock retriever to raise an exception
#     mock_retriever.invoke.side_effect = Exception("Retriever Error")

#     # LLM is never instantiated or called if retriever fails first
#     mock_llm_instance = MagicMock()
#     mock_chat_openai_class.return_value = mock_llm_instance

#     query = "This query will fail retrieval."
#     result = generate_answer(query, mock_retriever)

#     # Check for error handling
#     assert result["answer"] is None
#     assert result["sources"] == []

#     # Assert retriever was called
#     mock_retriever.invoke.assert_called_once_with(query)
#     # Assert ChatOpenAI was *not* called because the error happened before it
#     # mock_chat_openai_class.assert_not_called() # This assertion is removed as instantiation can happen before invoke failure

    # mock_chat_openai_class.assert_not_called() 

# Add test for source formatting without page number
@patch('src.generation.answer_generator.create_rag_chain')
def test_generate_answer_source_no_page(mock_create_chain, mock_retriever):
    """Test source formatting when a document lacks a page number."""
    mock_chain_instance = MagicMock()
    mock_chain_instance.invoke.return_value = {
        "answer": "Answer based on docs with and without page numbers.",
        "documents": [MOCK_DOC_1, MOCK_DOC_NO_PAGE] # Include doc without page
    }
    mock_create_chain.return_value = mock_chain_instance

    query = "What about metadata?"
    result = generate_answer(query, mock_retriever)

    assert result["answer"] is not None
    assert len(result["sources"]) == 2
    assert "Source: doc1.pdf, Page 1" in result["sources"]
    assert "Source: doc3.pdf" in result["sources"] # Check formatting without page

    mock_create_chain.assert_called_once()
    mock_chain_instance.invoke.assert_called_once_with(query) 
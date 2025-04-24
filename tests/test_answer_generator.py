import pytest
import os # Added os import
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS # Assuming FAISS is used, adjust if needed
from src.generation.answer_generator import create_rag_chain, generate_answer, format_docs


# Fixtures
@pytest.fixture
def mock_llm():
    """Fixture for a mocked LLM."""
    llm = MagicMock(spec=ChatOpenAI)
    # Mock the invoke method to return a specific string
    llm.invoke.return_value = "Mocked LLM Answer"
    return llm

@pytest.fixture
def mock_retriever():
    """Fixture for a mocked VectorStore that returns a mocked retriever interface."""
    # Create mock documents with metadata
    doc1 = Document(
        page_content="LangChain supports RAG.", 
        metadata={'source': 'docs/doc1.pdf', 'page': 1}
    )
    doc2 = Document(
        page_content="RAG combines retrieval and generation.", 
        metadata={'source': 'docs/doc2.pdf', 'page': 5}
    )
    doc3 = Document(
        page_content="Another fact.", 
        metadata={'source': 'docs/doc1.pdf', 'page': 2} # Same source, different page
    )
    mock_docs = [doc1, doc2, doc3]

    # Mock the retriever interface that the chain will use
    retriever_interface = MagicMock()
    retriever_interface.invoke.return_value = mock_docs # The retriever returns docs directly
    
    # Mock the VectorStore object passed to generate_answer
    mock_vector_store = MagicMock(spec=FAISS) 
    # Make generate_answer use the mocked retriever interface directly
    # (No need for .as_retriever() mock if generate_answer uses the passed object directly)
    # Update: generate_answer now uses the passed object directly as the interface
    # So we return the retriever_interface mock itself for generate_answer
    return retriever_interface

# --- Test format_docs --- 

def test_format_docs():
    """Test the format_docs utility function."""
    doc1 = Document(page_content="Content one.")
    doc2 = Document(page_content="Content two.")
    docs = [doc1, doc2]
    expected_output = "Content one.\n\nContent two."
    assert format_docs(docs) == expected_output

def test_format_docs_empty():
    """Test format_docs with an empty list."""
    assert format_docs([]) == ""

# --- Test create_rag_chain --- 

def test_create_rag_chain(mock_retriever, mock_llm):
    """Test the creation and structure of the RAG chain."""
    # The mock_retriever fixture now returns the retriever interface mock directly
    retriever_interface_mock = mock_retriever 
    
    # Pass the mocked interface to the chain creation function
    rag_chain = create_rag_chain(retriever_interface_mock, mock_llm)

    # Basic checks: Ensure it returns a runnable and has expected steps
    assert hasattr(rag_chain, 'invoke')
    # More specific checks could involve inspecting the chain's structure if needed

    # Test invocation with mocked components
    test_query = "What is RAG?"
    # The input to the chain is the query string
    chain_input = test_query
    result = rag_chain.invoke(chain_input)

    # Assert the retriever part was called (via the mocked interface invoke)
    # The input to the retriever part of the chain is the overall chain input
    retriever_interface_mock.invoke.assert_called_once_with(chain_input)

    # Assert the LLM was called (we check the final output)
    # The chain output is now a dict, check the answer key
    assert result["answer"] == "Mocked LLM Answer"
    mock_llm.invoke.assert_called_once()


# --- Test generate_answer --- 

@patch('src.generation.answer_generator.create_rag_chain') # Patch chain creation
@patch('src.generation.answer_generator.ChatOpenAI') # Patch LLM init
def test_generate_answer(MockChatOpenAI, MockCreateRagChain, mock_retriever):
    """Test the end-to-end generate_answer function with source attribution."""
    # Mock the RAG chain returned by create_rag_chain
    mock_rag_chain_instance = MagicMock()
    # The chain now returns a dictionary
    mock_chain_output = {
        'question': "Tell me about RAG.",
        'documents': mock_retriever.invoke.return_value, # Use the docs from the mocked retriever
        'answer': "RAG is great and uses sources."
    }
    mock_rag_chain_instance.invoke.return_value = mock_chain_output
    MockCreateRagChain.return_value = mock_rag_chain_instance
    
    mock_llm_instance = MagicMock()
    MockChatOpenAI.return_value = mock_llm_instance

    test_query = "Tell me about RAG."

    # Call the function under test
    result = generate_answer(test_query, mock_retriever) # Pass the retriever interface mock

    # Assertions
    # 1. Initialization checks
    MockChatOpenAI.assert_called_once_with(model_name='gpt-3.5-turbo', temperature=0)
    # No as_retriever call anymore in generate_answer
    # mock_retriever.as_retriever.assert_called_once()
    # retriever_interface = mock_retriever.as_retriever.return_value

    # 2. create_rag_chain call check (using the passed retriever interface)
    MockCreateRagChain.assert_called_once_with(mock_retriever, mock_llm_instance)

    # 3. Chain invocation check
    mock_rag_chain_instance.invoke.assert_called_once_with(test_query)

    # 4. Check the final returned dictionary structure and content
    assert isinstance(result, dict)
    assert result["answer"] == "RAG is great and uses sources."
    assert isinstance(result["sources"], list)
    # Check formatted sources (sorted)
    expected_sources = [
        "Source: doc1.pdf, Page 1",
        "Source: doc1.pdf, Page 2",
        "Source: doc2.pdf, Page 5",
    ]
    assert result["sources"] == expected_sources

@patch('src.generation.answer_generator.logging') # Patch logging
@patch('src.generation.answer_generator.create_rag_chain') # Patch chain creation
@patch('src.generation.answer_generator.ChatOpenAI') # Patch LLM init
def test_generate_answer_error_handling(MockChatOpenAI, MockCreateRagChain, MockLogging, mock_retriever):
    """Test generate_answer error handling returns the correct dict."""
    # Mock the RAG chain to raise an exception on invoke
    mock_rag_chain_instance = MagicMock()
    test_exception = ValueError("RAG chain failed!")
    mock_rag_chain_instance.invoke.side_effect = test_exception
    MockCreateRagChain.return_value = mock_rag_chain_instance
    
    mock_llm_instance = MagicMock()
    MockChatOpenAI.return_value = mock_llm_instance

    test_query = "This query will fail."

    # Call the function under test
    result = generate_answer(test_query, mock_retriever) # Pass the retriever interface mock

    # Assertions
    # 1. Chain invocation check
    mock_rag_chain_instance.invoke.assert_called_once_with(test_query)

    # 2. Logging check
    MockLogging.exception.assert_called_once()
    call_args, _ = MockLogging.exception.call_args
    assert f"Error generating answer for query: {test_query[:50]}" in call_args[0]

    # 3. Check that the function returned the specific error dictionary
    assert result == {"answer": None, "sources": []}

    # 4. Basic setup checks
    MockChatOpenAI.assert_called_once()
    # No as_retriever call anymore
    MockCreateRagChain.assert_called_once_with(mock_retriever, mock_llm_instance) 
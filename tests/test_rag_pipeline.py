import pytest
from unittest.mock import MagicMock, patch
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from src.generation.answer_generator import create_rag_chain, generate_answer, format_docs
from src.retrieval.vector_store import load_faiss_index, search_index

# Fixtures for testing the RAG pipeline
@pytest.fixture
def mock_documents():
    """Create mock documents for testing."""
    return [
        Document(page_content="RAG stands for Retrieval Augmented Generation.", 
                 metadata={"source": "test_doc1.pdf", "page": 1}),
        Document(page_content="RAG combines retrieval systems with generative models.", 
                 metadata={"source": "test_doc2.pdf", "page": 2}),
        Document(page_content="RAG helps ground LLMs in factual information.", 
                 metadata={"source": "test_doc3.pdf", "page": 3})
    ]

@pytest.fixture
def mock_vector_store(mock_documents):
    """Create a mock vector store that returns the mock documents."""
    mock_store = MagicMock(spec=FAISS)
    # Mock the as_retriever method to return a retriever interface
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = mock_documents
    mock_store.as_retriever.return_value = mock_retriever
    return mock_store

# Tests for the RAG pipeline
@patch('src.generation.answer_generator.create_rag_chain') # Patch chain creation
def test_rag_pipeline_end_to_end(mock_create_chain, mock_vector_store, mock_documents):
    """Test the end-to-end RAG pipeline with mocked components."""
    # Setup the mock chain
    mock_chain_instance = MagicMock()
    mock_chain_instance.invoke.return_value = {
        "answer": "RAG stands for Retrieval Augmented Generation. It combines retrieval systems with generative models.",
        "documents": mock_documents # Use the documents from fixture
    }
    mock_create_chain.return_value = mock_chain_instance

    # Test the pipeline
    query = "What is RAG?"
    # generate_answer expects the retriever interface directly now based on answer_generator code
    retriever_interface = mock_vector_store.as_retriever()
    result = generate_answer(query, retriever_interface)

    # Verify the result structure
    assert isinstance(result, dict)
    assert "answer" in result
    assert "sources" in result
    assert result["answer"] is not None
    assert len(result["sources"]) == 3 # Based on 3 mock documents

    # Verify create_rag_chain was called
    mock_create_chain.assert_called_once()
    # Verify the mock chain's invoke was called
    mock_chain_instance.invoke.assert_called_once_with(query)

@patch('src.generation.answer_generator.create_rag_chain') # Patch chain creation
def test_rag_pipeline_with_empty_results(mock_create_chain, mock_vector_store):
    """Test the RAG pipeline when no documents are retrieved."""
    # Setup the mock chain
    mock_chain_instance = MagicMock()
    mock_chain_instance.invoke.return_value = {
        "answer": "I cannot answer based on the provided information.",
        "documents": [] # Simulate empty retrieval result from chain
    }
    mock_create_chain.return_value = mock_chain_instance

    # Setup the retriever interface (though its invoke won't be called directly by generate_answer)
    retriever_interface = mock_vector_store.as_retriever()
    # We don't need to configure retriever_interface.invoke here as create_rag_chain is mocked

    # Test the pipeline
    query = "What is something not in the documents?"
    result = generate_answer(query, retriever_interface)

    # Verify the result
    assert result["answer"] == "I cannot answer based on the provided information."
    assert len(result["sources"]) == 0

    # Verify create_rag_chain was called
    mock_create_chain.assert_called_once()
    # Verify the mock chain's invoke was called
    mock_chain_instance.invoke.assert_called_once_with(query)

def test_rag_pipeline_error_handling():
    """Test error handling in the RAG pipeline."""
    # Create a retriever that raises an exception
    mock_retriever = MagicMock()
    mock_retriever.invoke.side_effect = Exception("Retrieval error")
    
    # Test the pipeline with the failing retriever
    query = "What is RAG?"
    result = generate_answer(query, mock_retriever)
    
    # Verify the error handling
    assert result["answer"] is None
    assert result["sources"] == []

def test_rag_chain_creation(mock_vector_store):
    """Test the creation of the RAG chain."""
    with patch('src.generation.answer_generator.ChatOpenAI') as MockChatOpenAI:
        # Setup the mock LLM
        mock_llm = MagicMock()
        MockChatOpenAI.return_value = mock_llm
        
        # Create the chain
        retriever = mock_vector_store.as_retriever()
        chain = create_rag_chain(retriever, mock_llm)
        
        # Verify the chain has the expected methods
        assert hasattr(chain, 'invoke')

def test_format_docs_with_various_inputs(mock_documents):
    """Test the format_docs function with various inputs."""
    # Test with normal documents
    formatted = format_docs(mock_documents)
    assert "RAG stands for" in formatted
    assert "combines retrieval" in formatted
    assert "ground LLMs" in formatted
    
    # Test with empty list
    assert format_docs([]) == ""
    
    # Test with a single document
    single_doc = [mock_documents[0]]
    assert format_docs(single_doc) == mock_documents[0].page_content

def test_search_index_integration(mock_vector_store, mock_documents):
    """Test the integration between search_index and the RAG pipeline."""
    with patch('src.retrieval.vector_store.FAISS') as MockFAISS:
        # Setup the mock FAISS index
        MockFAISS.load_local.return_value = mock_vector_store
        mock_vector_store.similarity_search.return_value = mock_documents
        
        # Mock the load_faiss_index function
        with patch('src.retrieval.vector_store.load_faiss_index', return_value=mock_vector_store):
            # Test the search_index function
            query = "What is RAG?"
            results = search_index(query, mock_vector_store)
            
            # Verify the results
            assert results == mock_documents
            mock_vector_store.similarity_search.assert_called_once()
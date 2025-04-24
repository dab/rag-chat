import pytest
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
    """Fixture for a mocked Retriever interface."""
    # Create mock documents
    doc1 = Document(page_content="LangChain supports RAG.", metadata={'source': 'doc1'})
    doc2 = Document(page_content="RAG combines retrieval and generation.", metadata={'source': 'doc2'})

    # Mock the retriever interface directly (e.g., VectorStoreRetriever)
    # The key methods used by the RAG chain are usually `invoke` or `get_relevant_documents`
    retriever_interface = MagicMock()
    # Mock the method the chain actually calls on the retriever part
    # In the current chain: {"context": retriever | format_docs, ...}
    # The retriever is called directly, likely via `invoke` implicitly by LCEL
    retriever_interface.invoke.return_value = [doc1, doc2]
    
    # We also need to mock the VectorStore object that generate_answer uses
    # to *get* the retriever interface via .as_retriever()
    mock_vector_store = MagicMock(spec=FAISS) # Mock the base VectorStore
    mock_vector_store.as_retriever.return_value = retriever_interface # Make .as_retriever() return our mocked interface

    # The test functions need the correct mock depending on what they test:
    # - create_rag_chain needs the retriever *interface* mock
    # - generate_answer needs the *vector store* mock
    # To simplify, let's return the vector store mock, as generate_answer needs it,
    # and adjust create_rag_chain test to use mock_vector_store.as_retriever()
    return mock_vector_store

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
    # Get the mocked retriever interface from the mocked vector store
    retriever_interface_mock = mock_retriever.as_retriever()
    
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
    assert result == "Mocked LLM Answer"
    mock_llm.invoke.assert_called_once()


# --- Test generate_answer --- 

@patch('src.generation.answer_generator.create_rag_chain') # Patch chain creation
@patch('src.generation.answer_generator.ChatOpenAI') # Patch LLM init
def test_generate_answer(MockChatOpenAI, MockCreateRagChain, mock_retriever):
    """Test the end-to-end generate_answer function with mocks."""
    # Mock the RAG chain returned by create_rag_chain
    mock_rag_chain_instance = MagicMock()
    mock_rag_chain_instance.invoke.return_value = "Final Mocked Answer"
    MockCreateRagChain.return_value = mock_rag_chain_instance
    
    # Mock the LLM instance (though it won't be directly used if chain is mocked)
    mock_llm_instance = MagicMock()
    MockChatOpenAI.return_value = mock_llm_instance

    test_query = "Tell me about RAG."

    # Call the function under test
    answer = generate_answer(test_query, mock_retriever)

    # Assertions
    # 1. Check if ChatOpenAI was initialized (still happens before create_rag_chain)
    MockChatOpenAI.assert_called_once_with(model_name='gpt-3.5-turbo', temperature=0)

    # 2. Check if as_retriever was called on the vector store mock
    mock_retriever.as_retriever.assert_called_once()
    retriever_interface = mock_retriever.as_retriever.return_value

    # 3. Check if create_rag_chain was called with the correct retriever interface and LLM
    MockCreateRagChain.assert_called_once_with(retriever_interface, mock_llm_instance)

    # 4. Check if the mocked chain's invoke was called with the query
    mock_rag_chain_instance.invoke.assert_called_once_with(test_query)

    # 5. Check the final returned answer
    assert answer == "Final Mocked Answer" 
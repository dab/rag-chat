# tests/retrieval/test_vector_store.py

import pytest
import os
from unittest.mock import patch, MagicMock

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS # Import needed for spec

# Assuming pytest-mock is installed via requirements or dev-requirements
# If not, use unittest.mock explicitly

# Mock the actual embedding/vector store classes before importing the module under test
MockHuggingFaceEmbeddings = MagicMock()
MockFAISS = MagicMock()

# Patch the classes where they are looked up in the module under test
# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.HuggingFaceEmbeddings', MockHuggingFaceEmbeddings) # Applied second, becomes first arg
def test_get_embedding_function_success(mock_embeddings_cls, mock_faiss_cls):
    """Test successful initialization of embeddings."""
    from src.retrieval.vector_store import get_embedding_function, DEFAULT_EMBEDDING_MODEL
    
    mock_instance = MagicMock()
    mock_embeddings_cls.return_value = mock_instance
    
    embeddings = get_embedding_function()
    
    assert embeddings == mock_instance
    mock_embeddings_cls.assert_called_once_with(model_name=DEFAULT_EMBEDDING_MODEL)

# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.get_embedding_function') # Applied second, becomes first arg
def test_build_faiss_index_success(mock_get_embeddings, mock_faiss_cls):
    """Test successful index building and saving."""
    from src.retrieval.vector_store import build_faiss_index
    
    mock_embed_func = MagicMock()
    mock_get_embeddings.return_value = mock_embed_func
    
    mock_faiss_instance = MagicMock()
    mock_faiss_cls.from_documents.return_value = mock_faiss_instance
    
    docs = [Document(page_content="doc1"), Document(page_content="doc2")]
    index_path = "./test_build_index"
    
    result = build_faiss_index(docs, index_path=index_path)
    
    assert result is True
    mock_get_embeddings.assert_called_once()
    mock_faiss_cls.from_documents.assert_called_once_with(docs, mock_embed_func)
    mock_faiss_instance.save_local.assert_called_once_with(index_path)

# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.get_embedding_function') # Applied second, becomes first arg
def test_build_faiss_index_build_error(mock_get_embeddings, mock_faiss_cls):
    """Test index build failure during FAISS.from_documents."""
    from src.retrieval.vector_store import build_faiss_index
    mock_get_embeddings.return_value = MagicMock()
    mock_faiss_cls.from_documents.side_effect = Exception("Build failed")
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.get_embedding_function') # Applied second, becomes first arg
def test_build_faiss_index_save_error(mock_get_embeddings, mock_faiss_cls):
    """Test index build failure during save_local."""
    from src.retrieval.vector_store import build_faiss_index
    mock_get_embeddings.return_value = MagicMock()
    mock_faiss_instance = MagicMock()
    mock_faiss_instance.save_local.side_effect = Exception("Save failed")
    mock_faiss_cls.from_documents.return_value = mock_faiss_instance
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.get_embedding_function') # Applied second, becomes second arg
@patch('os.path.exists') # Applied third, becomes first arg
def test_load_faiss_index_success(mock_exists, mock_get_embeddings, mock_faiss_cls):
    """Test successful index loading."""
    from src.retrieval.vector_store import load_faiss_index
    
    mock_exists.return_value = True # Assume index files exist
    mock_embed_func = MagicMock()
    mock_get_embeddings.return_value = mock_embed_func
    
    mock_loaded_index = MagicMock()
    mock_faiss_cls.load_local.return_value = mock_loaded_index
    
    index_path = "./test_load_index"
    result = load_faiss_index(index_path=index_path)
    
    assert result == mock_loaded_index
    mock_exists.assert_called()
    mock_get_embeddings.assert_called_once()
    mock_faiss_cls.load_local.assert_called_once_with(
        index_path, mock_embed_func, allow_dangerous_deserialization=True
    )

# Order matters: arguments correspond bottom-up
@patch('src.retrieval.vector_store.FAISS', MockFAISS) # Applied first, becomes last arg
@patch('src.retrieval.vector_store.get_embedding_function') # Applied second, becomes second arg
@patch('os.path.exists') # Applied third, becomes first arg
def test_load_faiss_index_load_error(mock_exists, mock_get_embeddings, mock_faiss_cls):
    """Test index loading failure during FAISS.load_local."""
    from src.retrieval.vector_store import load_faiss_index
    mock_exists.return_value = True
    mock_get_embeddings.return_value = MagicMock()
    mock_faiss_cls.load_local.side_effect = Exception("Load error")
    result = load_faiss_index()
    assert result is None

# --- Tests needing only local context or direct function calls --- 

@patch('src.retrieval.vector_store.HuggingFaceEmbeddings', MockHuggingFaceEmbeddings)
def test_get_embedding_function_failure(mock_embeddings_cls):
    """Test failure during embedding initialization."""
    from src.retrieval.vector_store import get_embedding_function
    mock_embeddings_cls.side_effect = Exception("Model load error")
    embeddings = get_embedding_function()
    assert embeddings is None

@patch('src.retrieval.vector_store.get_embedding_function')
def test_build_faiss_index_no_embeddings(mock_get_embeddings):
    """Test index build failure when embeddings fail."""
    from src.retrieval.vector_store import build_faiss_index
    mock_get_embeddings.return_value = None
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

@patch('os.path.exists')
def test_load_faiss_index_not_found(mock_exists):
    """Test index loading failure when files don't exist."""
    from src.retrieval.vector_store import load_faiss_index
    mock_exists.return_value = False
    result = load_faiss_index()
    assert result is None

@patch('os.path.exists')
@patch('src.retrieval.vector_store.get_embedding_function')
def test_load_faiss_index_no_embeddings(mock_get_embeddings, mock_exists):
    """Test index loading failure when embeddings fail."""
    from src.retrieval.vector_store import load_faiss_index
    mock_exists.return_value = True
    mock_get_embeddings.return_value = None
    result = load_faiss_index()
    assert result is None

# --- Tests for search_index (no patching needed at decorator level) ---

def test_search_index_success():
    """Test successful similarity search."""
    from src.retrieval.vector_store import search_index
    mock_index = MagicMock(spec=FAISS) # Use spec for type hinting
    expected_docs = [Document(page_content="result1"), Document(page_content="result2")]
    mock_index.similarity_search.return_value = expected_docs
    
    query = "test query"
    top_k = 2
    results = search_index(query, mock_index, top_k=top_k)
    
    assert results == expected_docs
    mock_index.similarity_search.assert_called_once_with(query, k=top_k)

def test_search_index_no_index():
    """Test search failure with invalid index."""
    from src.retrieval.vector_store import search_index
    results = search_index("test", None)
    assert results == []

def test_search_index_search_error():
    """Test search failure during similarity_search."""
    from src.retrieval.vector_store import search_index
    mock_index = MagicMock(spec=FAISS)
    mock_index.similarity_search.side_effect = Exception("Search failed")
    results = search_index("test", mock_index)
    assert results == []

def test_get_embedding_function_success(mocker):
    """Test successful initialization of embeddings using mocker."""
    # Patch the class *before* importing the function that uses it
    MockEmbeddingsCls = mocker.patch('src.retrieval.vector_store.HuggingFaceEmbeddings')
    # Import after patching
    from src.retrieval.vector_store import get_embedding_function, DEFAULT_EMBEDDING_MODEL

    mock_instance = MagicMock()
    MockEmbeddingsCls.return_value = mock_instance

    embeddings = get_embedding_function()

    assert embeddings == mock_instance
    MockEmbeddingsCls.assert_called_once_with(model_name=DEFAULT_EMBEDDING_MODEL)

def test_get_embedding_function_failure(mocker):
    """Test failure during embedding initialization using mocker."""
    MockEmbeddingsCls = mocker.patch('src.retrieval.vector_store.HuggingFaceEmbeddings')
    from src.retrieval.vector_store import get_embedding_function

    MockEmbeddingsCls.side_effect = Exception("Model load error")

    embeddings = get_embedding_function()

    assert embeddings is None

def test_build_faiss_index_success(mocker):
    """Test successful index building and saving using mocker."""
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    MockFAISSCls = mocker.patch('src.retrieval.vector_store.FAISS')
    from src.retrieval.vector_store import build_faiss_index

    mock_embed_func = MagicMock()
    mock_get_embeddings.return_value = mock_embed_func

    mock_faiss_instance = MagicMock()
    MockFAISSCls.from_documents.return_value = mock_faiss_instance

    docs = [Document(page_content="doc1"), Document(page_content="doc2")]
    index_path = "./test_build_index"

    result = build_faiss_index(docs, index_path=index_path)

    assert result is True
    mock_get_embeddings.assert_called_once()
    MockFAISSCls.from_documents.assert_called_once_with(docs, mock_embed_func)
    mock_faiss_instance.save_local.assert_called_once_with(index_path)

def test_build_faiss_index_no_embeddings(mocker):
    """Test index build failure when embeddings fail using mocker."""
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    from src.retrieval.vector_store import build_faiss_index

    mock_get_embeddings.return_value = None
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

def test_build_faiss_index_build_error(mocker):
    """Test index build failure during FAISS.from_documents using mocker."""
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    MockFAISSCls = mocker.patch('src.retrieval.vector_store.FAISS')
    from src.retrieval.vector_store import build_faiss_index

    mock_get_embeddings.return_value = MagicMock()
    MockFAISSCls.from_documents.side_effect = Exception("Build failed")
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

def test_build_faiss_index_save_error(mocker):
    """Test index build failure during save_local using mocker."""
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    MockFAISSCls = mocker.patch('src.retrieval.vector_store.FAISS')
    from src.retrieval.vector_store import build_faiss_index

    mock_get_embeddings.return_value = MagicMock()
    mock_faiss_instance = MagicMock()
    mock_faiss_instance.save_local.side_effect = Exception("Save failed")
    MockFAISSCls.from_documents.return_value = mock_faiss_instance
    result = build_faiss_index([Document(page_content="test")])
    assert result is False

def test_load_faiss_index_success(mocker):
    """Test successful index loading using mocker."""
    mock_exists = mocker.patch('os.path.exists')
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    MockFAISSCls = mocker.patch('src.retrieval.vector_store.FAISS')
    from src.retrieval.vector_store import load_faiss_index

    mock_exists.return_value = True # Assume index files exist
    mock_embed_func = MagicMock()
    mock_get_embeddings.return_value = mock_embed_func

    mock_loaded_index = MagicMock()
    MockFAISSCls.load_local.return_value = mock_loaded_index

    index_path = "./test_load_index"
    result = load_faiss_index(index_path=index_path)

    assert result == mock_loaded_index
    # Check os.path.exists called for both index.faiss and index.pkl
    assert mock_exists.call_count >= 2
    mock_get_embeddings.assert_called_once()
    MockFAISSCls.load_local.assert_called_once_with(
        index_path, mock_embed_func, allow_dangerous_deserialization=True
    )

def test_load_faiss_index_not_found(mocker):
    """Test index loading failure when files don't exist using mocker."""
    mock_exists = mocker.patch('os.path.exists')
    from src.retrieval.vector_store import load_faiss_index

    mock_exists.return_value = False
    result = load_faiss_index()
    assert result is None

def test_load_faiss_index_no_embeddings(mocker):
    """Test index loading failure when embeddings fail using mocker."""
    mock_exists = mocker.patch('os.path.exists')
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    from src.retrieval.vector_store import load_faiss_index

    mock_exists.return_value = True
    mock_get_embeddings.return_value = None
    result = load_faiss_index()
    assert result is None

def test_load_faiss_index_load_error(mocker):
    """Test index loading failure during FAISS.load_local using mocker."""
    mock_exists = mocker.patch('os.path.exists')
    mock_get_embeddings = mocker.patch('src.retrieval.vector_store.get_embedding_function')
    MockFAISSCls = mocker.patch('src.retrieval.vector_store.FAISS')
    from src.retrieval.vector_store import load_faiss_index

    mock_exists.return_value = True
    mock_get_embeddings.return_value = MagicMock()
    MockFAISSCls.load_local.side_effect = Exception("Load error")
    result = load_faiss_index()
    assert result is None

# --- Tests for search_index (no patching needed at decorator level) ---

def test_search_index_success(mocker): # Added mocker fixture just in case
    """Test successful similarity search."""
    from src.retrieval.vector_store import search_index
    mock_index = MagicMock(spec=FAISS) # Use spec for type hinting
    expected_docs = [Document(page_content="result1"), Document(page_content="result2")]
    mock_index.similarity_search.return_value = expected_docs

    query = "test query"
    top_k = 2
    results = search_index(query, mock_index, top_k=top_k)

    assert results == expected_docs
    mock_index.similarity_search.assert_called_once_with(query, k=top_k)

def test_search_index_no_index(mocker): # Added mocker fixture just in case
    """Test search failure with invalid index."""
    from src.retrieval.vector_store import search_index
    results = search_index("test", None)
    assert results == []

def test_search_index_search_error(mocker): # Added mocker fixture just in case
    """Test search failure during similarity_search."""
    from src.retrieval.vector_store import search_index
    mock_index = MagicMock(spec=FAISS)
    mock_index.similarity_search.side_effect = Exception("Search failed")
    results = search_index("test", mock_index)
    assert results == []

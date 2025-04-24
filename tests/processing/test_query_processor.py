# tests/processing/test_query_processor.py

import pytest
from src.processing.query_processor import process_query
from unittest.mock import MagicMock

EXPECTED_SYSTEM_MSG = "System: You are a helpful assistant."

def test_process_query_normal():
    """Test processing a standard query."""
    query = "What is RAG?"
    expected_output = f"{EXPECTED_SYSTEM_MSG}\nHuman: {query}"
    assert process_query(f"  {query}  ") == expected_output

def test_process_query_no_extra_whitespace():
    """Test processing a query with no leading/trailing whitespace."""
    query = "Explain LangChain"
    expected_output = f"{EXPECTED_SYSTEM_MSG}\nHuman: {query}"
    assert process_query(query) == expected_output

def test_process_query_only_whitespace():
    """Test processing a query that is only whitespace."""
    with pytest.raises(ValueError, match="Query cannot be empty after stripping."):
        process_query("   \t\n  ")

def test_process_query_empty_string():
    """Test processing an empty string query."""
    with pytest.raises(ValueError, match="Query cannot be empty after stripping."):
        process_query("")

def test_process_query_none():
    """Test processing a None query."""
    with pytest.raises(ValueError, match="Query cannot be None."):
        process_query(None)

def test_process_query_with_internal_whitespace():
    """Test processing query with internal spaces preserved."""
    query = "tell me   about   pdfs"
    expected_output = f"{EXPECTED_SYSTEM_MSG}\nHuman: {query}"
    assert process_query(f"  {query}  ") == expected_output

# Test for LangChain invocation error
def test_process_query_langchain_invoke_error(mocker):
    """Test error handling when prompt.invoke fails."""
    # Mock the ChatPromptTemplate.from_messages to return a mock prompt
    mock_prompt = MagicMock()
    # Configure the invoke method on the mock prompt to raise an error
    mock_prompt.invoke.side_effect = Exception("LangChain Invoke Failed")
    mocker.patch('langchain_core.prompts.ChatPromptTemplate.from_messages', return_value=mock_prompt)

    # Expect a RuntimeError to be raised by process_query
    with pytest.raises(RuntimeError, match="Failed to format query using LangChain: LangChain Invoke Failed"):
        process_query("A valid query that will fail invocation")

    # Verify that the mock prompt's invoke was called
    mock_prompt.invoke.assert_called_once_with({"user_input": "A valid query that will fail invocation"}) 
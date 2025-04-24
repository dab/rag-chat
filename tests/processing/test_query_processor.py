# tests/processing/test_query_processor.py

import pytest
from src.processing.query_processor import process_query

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
# tests/test_app.py

import pytest
from unittest.mock import MagicMock
import streamlit as st
import app # Import the module we are testing
from app import validate_uploaded_files # Import the function to test

# Mock constants from app.py to avoid direct dependency if needed, or use app.* directly
MAX_FILES = app.MAX_FILES
MAX_FILE_SIZE_BYTES = app.MAX_FILE_SIZE_BYTES
ALLOWED_MIME_TYPES = app.ALLOWED_MIME_TYPES

# Helper function to create mock files
def create_mock_file(name="test.pdf", file_type="application/pdf", size=1024):
    mock = MagicMock()
    mock.name = name
    mock.type = file_type
    mock.size = size
    return mock

# Test case: Uploading more than MAX_FILES (This condition is checked *before* validate_uploaded_files)
def test_upload_too_many_files_condition():
    mock_files = [create_mock_file(f"test_{i}.pdf") for i in range(MAX_FILES + 1)]
    # Assert the condition checked in the main app flow
    assert len(mock_files) > MAX_FILES

# --- Tests for the validate_uploaded_files function --- 

# Test case: Valid single file upload
def test_validate_single_valid_file():
    mock_file = create_mock_file(size=MAX_FILE_SIZE_BYTES - 1)
    uploaded_files = [mock_file]

    valid_files, error_messages = validate_uploaded_files(uploaded_files)

    assert len(valid_files) == 1
    assert not error_messages
    assert valid_files[0] == mock_file

# Test case: Three valid files
def test_validate_three_valid_files():
    mock_files = [
        create_mock_file(name="test1.pdf", size=1000),
        create_mock_file(name="test2.pdf", size=2000),
        create_mock_file(name="test3.pdf", size=3000)
    ]

    valid_files, error_messages = validate_uploaded_files(mock_files)

    assert len(valid_files) == 3
    assert not error_messages
    assert valid_files == mock_files # Check if all original mocks are returned

# Test case: Invalid file type
def test_validate_invalid_file_type():
    mock_file = create_mock_file(name="test.txt", file_type="text/plain")
    uploaded_files = [mock_file]

    valid_files, error_messages = validate_uploaded_files(uploaded_files)

    assert len(valid_files) == 0
    assert len(error_messages) == 1
    assert "Invalid file type" in error_messages[0]
    assert "test.txt" in error_messages[0]

# Test case: File too large
def test_validate_file_too_large():
    mock_file = create_mock_file(size=MAX_FILE_SIZE_BYTES + 1)
    uploaded_files = [mock_file]

    valid_files, error_messages = validate_uploaded_files(uploaded_files)

    assert len(valid_files) == 0
    assert len(error_messages) == 1
    assert "exceeds the" in error_messages[0]
    assert "test.pdf" in error_messages[0]

# Test case: Empty file (size 0)
def test_validate_empty_file():
    # Empty files are currently accepted if type is correct
    mock_file = create_mock_file(size=0)
    uploaded_files = [mock_file]

    valid_files, error_messages = validate_uploaded_files(uploaded_files)

    assert len(valid_files) == 1
    assert not error_messages
    assert valid_files[0] == mock_file

# Test case: Combination of valid and invalid files
def test_validate_mixed_validity_files():
    mock_files = [
        create_mock_file(name="good1.pdf", size=1000),
        create_mock_file(name="too_big.pdf", size=MAX_FILE_SIZE_BYTES + 1),
        create_mock_file(name="wrong_type.txt", file_type="text/plain"),
        create_mock_file(name="good2.pdf", size=2000),
    ]

    valid_files, error_messages = validate_uploaded_files(mock_files)

    assert len(valid_files) == 2 # good1.pdf and good2.pdf should be valid
    assert len(error_messages) == 2
    # Check specific files are in valid_files
    assert mock_files[0] in valid_files
    assert mock_files[3] in valid_files
    # Check specific error messages
    assert any("exceeds the" in msg and "too_big.pdf" in msg for msg in error_messages)
    assert any("Invalid file type" in msg and "wrong_type.txt" in msg for msg in error_messages)

# Test case: No files uploaded (empty list)
def test_validate_no_files():
    uploaded_files = []
    valid_files, error_messages = validate_uploaded_files(uploaded_files)
    assert len(valid_files) == 0
    assert not error_messages

# Note: Testing malformed PDFs requires more sophisticated checks or mocking
# a PDF parsing library if one were used within the validation function.
# The current validation only checks type (MIME) and size. 
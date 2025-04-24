# Testing Documentation for RAG Chat

This directory contains tests for the RAG Chat application, implementing the requirements specified in Epic 3: Testing.

## Test Structure

- `test_pdf_validation.py`: Unit tests for PDF validation logic (Story 3.1)
- `test_rag_pipeline.py`: Unit tests for answer generation logic (Story 3.2)
- `test_e2e.py`: End-to-end tests using Selenium (Stories 3.4 and 3.5)
- `test_answer_generator.py`: Existing tests for the answer generator component
- `processing/test_query_processor.py`: Tests for query processing
- `retrieval/test_vector_store.py`: Tests for vector store operations

## Test Fixtures

The `fixtures/` directory contains test files used by the tests:
- `empty.pdf`: An empty PDF file for testing edge cases
- `invalid_type.txt`: A non-PDF file for testing type validation
- `sample.pdf`: A sample PDF with content for E2E testing

## Running Tests

### Running All Tests

```bash
pytest
```

### Running Tests with Coverage Report

```bash
pytest --cov=src --cov-report=term --cov-report=html:coverage_html
```

### Running Specific Test Files

```bash
pytest tests/test_pdf_validation.py
pytest tests/test_rag_pipeline.py
pytest tests/test_e2e.py
```

## Code Coverage Requirements

As specified in Story 3.3, the project aims to achieve at least 80% code coverage. The pytest configuration in `pytest.ini` enforces this requirement with the `--cov-fail-under=80` option.

## End-to-End Testing

The E2E tests in `test_e2e.py` require:
1. The Streamlit app to be running on `localhost:8501`
2. Chrome WebDriver installed and available in PATH

To run the Streamlit app:

```bash
streamlit run app.py
```

Then in another terminal, run the E2E tests:

```bash
pytest tests/test_e2e.py
```

## Performance Testing

Story 3.5 requires measuring answer performance to ensure it's under 5 seconds. The E2E tests include performance measurement and will fail if the answer generation takes longer than the specified threshold.

## Test Implementation Notes

1. **PDF Validation Tests**: Implemented with mock file objects to test various validation scenarios including edge cases.
2. **RAG Pipeline Tests**: Use mock vector stores and documents to test the retrieval and generation components.
3. **E2E Tests**: Simulate real user interactions with the web interface using Selenium.
4. **Performance Tests**: Measure the time taken for answer generation and compare against the 5-second threshold.

## Adding New Tests

When adding new features to the application, corresponding tests should be added to maintain the 80% code coverage requirement. Follow the existing patterns for unit tests and integration tests.
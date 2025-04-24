# Story 3.4: Automate End-to-End Tests with Selenium

## Story

**As a** QA engineer
**I want** to automate end-to-end tests using Selenium
**so that** the full user flow (upload, query, answer) is verified.

## Status

In-Progress

## Context

With unit tests covering individual components, this story focuses on verifying the complete user journey through the application using end-to-end (E2E) tests. The PRD specifies using Selenium for browser automation. An existing test file (`tests/test_e2e.py`) contains preliminary Selenium tests, which are currently skipped. This story involves ensuring the necessary environment (Selenium, WebDriver, potentially a running instance of the Streamlit app) is configured, activating and refining the existing tests, and potentially adding more to cover the primary scenarios: loading the app, uploading valid PDFs, submitting a query, and receiving an answer with sources. This provides confidence that the integrated application works as expected from a user's perspective.

## Estimation

Story Points: 3 (Requires environment setup, running the app, and Selenium test execution/debugging)

## Acceptance Criteria

1.  - [ ] Selenium and necessary WebDriver (e.g., ChromeDriver) are installed and configured in the environment.
2.  - [ ] The Streamlit application (`app.py`) can be run locally for testing purposes.
3.  - [ ] The E2E tests in `tests/test_e2e.py` are un-skipped and updated as needed.
4.  - [ ] E2E tests successfully simulate: 
    *   Loading the application page.
    *   Uploading one or more valid PDF files.
    *   Submitting a query related to the uploaded PDFs.
    *   Receiving a visible answer and source attribution on the page.
5.  - [ ] The E2E test suite passes when run against the locally running application.

## Subtasks

1.  - [ ] **Setup E2E Environment:**
    1.  - [ ] Verify `selenium` is in `requirements.txt` (already added).
    2.  - [ ] Ensure necessary WebDriver (e.g., ChromeDriver) is installed and accessible in the system's PATH or configured via WebDriver manager/options.
    3.  - [ ] Document steps for running the Streamlit app locally (e.g., `streamlit run app.py`).
2.  - [ ] **Prepare E2E Tests:**
    1.  - [ ] Review `tests/test_e2e.py`.
    2.  - [ ] Remove `@pytest.mark.skip` decorators from relevant tests (e.g., `test_app_loads`, `test_pdf_upload`, `test_query_and_answer`).
    3.  - [ ] Update test locators (e.g., CSS selectors, XPaths) if UI structure has changed.
    4.  - [ ] Ensure test uses appropriate waits (WebDriverWait) for elements to appear, especially after file uploads and query submissions.
    5.  - [ ] Verify test uses a valid, existing test PDF file (e.g., `tests/fixtures/sample.pdf`).
3.  - [ ] **Execute E2E Tests:**
    1.  - [ ] Start the Streamlit application locally.
    2.  - [ ] Run the E2E tests (e.g., `python -m pytest tests/test_e2e.py`).
    3.  - [ ] Debug and fix any test failures related to element interaction, timing, or assertions.
4.  - [ ] **Verify and Conclude:**
    1.  - [ ] Confirm the E2E test suite passes reliably against the local app.

## Testing Requirements:

*   End-to-end tests using Pytest and Selenium.
*   Requires a running instance of the Streamlit application.
*   Requires WebDriver installation and configuration.

## Story Wrap Up (To be filled in AFTER agent execution):

*   **Agent Model Used:** `<Agent Model Name/Version>`
*   **Agent Credit or Cost:** `<Cost/Credits Consumed>`
*   **Date/Time Completed:** `<Timestamp>`
*   **Commit Hash:** `<Git Commit Hash of resulting code>`
*   **Change Log**
    *   change X
    *   change Y
    ... 
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Constants
APP_URL = "http://localhost:8501"  # Default Streamlit port
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample.pdf")
PERFORMANCE_THRESHOLD_SECONDS = 5  # Performance requirement from Story 3.5

# Fixtures
@pytest.mark.skip(reason="Skipping E2E setup for unit test focus")
@pytest.fixture(scope="module")
def driver():
    """Setup and teardown for Selenium WebDriver."""
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)  # Set implicit wait timeout
    
    yield driver
    
    # Teardown
    driver.quit()

# Helper functions
def wait_for_element(driver, by, value, timeout=10):
    """Wait for an element to be present and visible."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        pytest.fail(f"Element not found: {by}={value}")

# End-to-end tests
@pytest.mark.skip(reason="Skipping E2E test for unit test focus")
def test_app_loads(driver):
    """Test that the application loads successfully."""
    driver.get(APP_URL)
    assert "RAG Chat" in driver.title or "RAG Chat" in driver.page_source
    
    # Verify main components are present
    wait_for_element(driver, By.XPATH, "//h1[contains(text(), 'RAG Chat')]")
    wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Upload your PDF documents')]")
    wait_for_element(driver, By.TAG_NAME, "input")  # File upload input
    wait_for_element(driver, By.XPATH, "//input[@type='text']")  # Query input

@pytest.mark.skip(reason="Skipping E2E test for unit test focus")
@pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF not found")
def test_pdf_upload(driver):
    """Test PDF upload functionality."""
    driver.get(APP_URL)
    
    # Find the file upload input and upload the test PDF
    file_input = wait_for_element(driver, By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(TEST_PDF_PATH)
    
    # Wait for upload success message
    success_message = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Successfully validated')]")
    assert "Successfully validated" in success_message.text
    
    # Verify the file name appears in the success message
    assert os.path.basename(TEST_PDF_PATH) in driver.page_source

@pytest.mark.skip(reason="Skipping E2E test for unit test focus")
@pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF not found")
def test_query_and_answer(driver):
    """Test the full query and answer flow with performance measurement."""
    driver.get(APP_URL)
    
    # Upload PDF first
    file_input = wait_for_element(driver, By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(TEST_PDF_PATH)
    wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Successfully validated')]")
    
    # Enter a query
    query_input = wait_for_element(driver, By.XPATH, "//input[@type='text']")
    test_query = "What is RAG?"
    query_input.send_keys(test_query)
    query_input.submit()  # Submit the form
    
    # Start timing for performance measurement
    start_time = time.time()
    
    # Wait for processing message
    wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Processing query')]")
    
    # Wait for answer to appear
    answer_element = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Generated Answer')]")
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Verify answer appears
    assert answer_element is not None
    
    # Check performance against threshold (Story 3.5)
    assert response_time < PERFORMANCE_THRESHOLD_SECONDS, \
        f"Answer generation took {response_time:.2f}s, exceeding the {PERFORMANCE_THRESHOLD_SECONDS}s threshold"
    
    # Log the performance for reporting
    print(f"Answer generation performance: {response_time:.2f} seconds")
    
    # Verify sources are displayed
    sources_element = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Source:')]")
    assert sources_element is not None

@pytest.mark.skip(reason="Skipping E2E test for unit test focus")
def test_error_handling(driver):
    """Test error handling for invalid inputs."""
    driver.get(APP_URL)
    
    # Test empty query
    query_input = wait_for_element(driver, By.XPATH, "//input[@type='text']")
    query_input.send_keys("  ")  # Just spaces
    query_input.submit()
    
    # Should show a warning about no documents
    warning = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Please upload valid PDF')]")
    assert warning is not None
    
    # Test query without documents
    query_input.clear()
    query_input.send_keys("What is RAG?")
    query_input.submit()
    
    # Should show a warning about no documents
    warning = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Please upload valid PDF')]")
    assert warning is not None

# Run the tests with: pytest -v tests/test_e2e.py
# Note: The Streamlit app must be running on localhost:8501 for these tests to work
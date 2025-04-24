import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Constants
APP_URL = "http://localhost:8501"  # Default Streamlit port
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample.pdf")
PERFORMANCE_THRESHOLD_SECONDS = 5  # Performance requirement from Story 3.5

# Fixtures
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
        pytest.fail(f"Element not found: {by}={value} within {timeout} seconds")

# End-to-end tests
def test_app_loads(driver):
    """Test that the application loads successfully."""
    driver.get(APP_URL)
    
    # Verify main components are present using new selectors
    wait_for_element(driver, By.XPATH, "//*[@id='rag-chat']") # Main title
    wait_for_element(driver, By.XPATH, "//div[@data-testid='stMarkdownContainer']//p[contains(text(), 'Upload your PDF documents')]") # Upload instruction
    wait_for_element(driver, By.XPATH, "//input[@data-testid='stFileUploaderDropzoneInput']") # File upload input
    wait_for_element(driver, By.XPATH, "//div[@data-testid='stTextInputRootElement']//input[@type='text']") # Query input

@pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF not found")
def test_pdf_upload(driver):
    """Test PDF upload functionality."""
    driver.get(APP_URL)
    
    # Find the file upload input using new selector and upload the test PDF
    file_input = wait_for_element(driver, By.XPATH, "//input[@data-testid='stFileUploaderDropzoneInput']")
    file_input.send_keys(TEST_PDF_PATH)
    
    # Wait for upload success message using new selector (Increased timeout)
    success_message_div = wait_for_element(driver, By.XPATH, "//div[@data-testid='stAlertContentSuccess']", timeout=20)
    # Assert specific text within the success alert
    assert "Successfully validated" in success_message_div.text

@pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF not found")
def test_query_and_answer(driver):
    """Test the full query and answer flow with performance measurement."""
    driver.get(APP_URL)
    
    # Upload PDF first using new selectors
    file_input = wait_for_element(driver, By.XPATH, "//input[@data-testid='stFileUploaderDropzoneInput']")
    file_input.send_keys(TEST_PDF_PATH)
    # Wait for success message using new selector
    wait_for_element(driver, By.XPATH, "//div[@data-testid='stAlertContentSuccess']", timeout=20)
    
    # Enter a query using new selector
    query_input = wait_for_element(driver, By.XPATH, "//div[@data-testid='stTextInputRootElement']//input[@type='text']")
    test_query = "What is RAG?"
    query_input.send_keys(test_query)
    query_input.send_keys(Keys.RETURN) # Use Enter key
    
    # Start timing for performance measurement
    start_time = time.time()
    
    # Wait for processing message (Assuming this text still exists somewhere)
    # If this fails, we may need a specific selector for the spinner/processing state
    wait_for_element(driver, By.XPATH, "//*[contains(text(), 'Processing query')]", timeout=5) # Short timeout ok?
    
    # Wait for answer to appear using new assumed selector
    answer_element = wait_for_element(driver, By.XPATH, "//div[@data-testid='stMarkdownContainer'][contains(., 'Generated Answer')]", timeout=20)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Verify answer appears
    assert answer_element is not None
    assert "Generated Answer" in answer_element.text # Check text within the container
    
    # Check performance against threshold (Story 3.5)
    assert response_time < PERFORMANCE_THRESHOLD_SECONDS, \
        f"Answer generation took {response_time:.2f}s, exceeding the {PERFORMANCE_THRESHOLD_SECONDS}s threshold"
    
    # Log the performance for reporting
    print(f"Answer generation performance: {response_time:.2f} seconds")
    
    # Verify sources are displayed using new assumed selector
    sources_element = wait_for_element(driver, By.XPATH, "//div[@data-testid='stMarkdownContainer'][contains(., 'Source:')]")
    assert sources_element is not None
    assert "Source:" in sources_element.text # Check text within the container

def test_error_handling(driver):
    """Test error handling for invalid inputs."""
    driver.get(APP_URL)
    
    # Test empty query using new selector
    query_input = wait_for_element(driver, By.XPATH, "//div[@data-testid='stTextInputRootElement']//input[@type='text']")
    query_input.send_keys("  ")  # Just spaces
    query_input.send_keys(Keys.RETURN) # Use Enter key
    
    # Should show a warning about no documents using new selector
    warning_div = wait_for_element(driver, By.XPATH, "//div[@data-testid='stAlertContentWarning']")
    # Assert specific text within the warning alert
    assert "Please upload valid PDF" in warning_div.text
    assert warning_div is not None
    
    # Test query without documents
    query_input.clear()
    query_input.send_keys("What is RAG?")
    query_input.send_keys(Keys.RETURN) # Use Enter key
    
    # Should show a warning about no documents using new selector
    warning_div = wait_for_element(driver, By.XPATH, "//div[@data-testid='stAlertContentWarning']")
     # Assert specific text within the warning alert
    assert "Please upload valid PDF" in warning_div.text
    assert warning_div is not None

# Run the tests with: pytest -v tests/test_e2e.py
# Note: The Streamlit app must be running on localhost:8501 for these tests to work
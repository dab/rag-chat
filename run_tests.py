#!/usr/bin/env python3
"""
Test runner script for RAG Chat application.

This script runs all tests and generates a coverage report to ensure
the codebase meets the 80% code coverage requirement specified in Story 3.3.

Usage:
    python run_tests.py [--e2e] [--html]

Options:
    --e2e: Include end-to-end tests (requires Streamlit app running)
    --html: Generate HTML coverage report
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Run tests for RAG Chat application")
    parser.add_argument("--e2e", action="store_true", help="Include end-to-end tests")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    args = parser.parse_args()
    
    # Base command
    cmd = ["pytest", "-v"]
    
    # Add coverage options
    cmd.extend(["--cov=src", "--cov-report=term"])
    if args.html:
        cmd.append("--cov-report=html:coverage_html")
    
    # Add coverage threshold
    cmd.append("--cov-fail-under=80")
    
    # Exclude E2E tests by default
    if not args.e2e:
        cmd.append("--ignore=tests/test_e2e.py")
        print("Excluding E2E tests. Use --e2e to include them.")
    else:
        print("Including E2E tests. Make sure the Streamlit app is running.")
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Print summary
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if result.returncode == 0 and not args.e2e:
            print("\nNote: E2E tests were not run. Use --e2e to include them.")
    else:
        print("\n❌ Some tests failed or coverage threshold not met.")
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
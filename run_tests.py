#!/usr/bin/env python3
"""
Test runner for the IPA transcription system
Can be run without pytest if needed

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py test_json_ipa # Run specific test file
"""

import sys
import os
import unittest
import importlib.util

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all tests using unittest if pytest is not available"""
    
    # Try to use pytest if available
    try:
        import pytest
        print("Running tests with pytest...")
        return pytest.main(["-v", "tests/"])
    except ImportError:
        print("pytest not found, running with unittest...")
        return run_with_unittest()

def run_with_unittest():
    """Run tests using built-in unittest"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_file):
    """Run a specific test file"""
    try:
        import pytest
        return pytest.main(["-v", f"tests/{test_file}"])
    except ImportError:
        # Load and run specific test with unittest
        spec = importlib.util.spec_from_file_location("test_module", f"tests/{test_file}")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1

def main():
    """Main test runner"""
    print("=== IPA Transcription System Test Runner ===")
    print("Comprehensive unit tests for JsonIPA and Wikipron classes")
    print("Tests cover: Core functionality, Error handling, Performance, Edge cases")
    print()
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not test_file.endswith('.py'):
            test_file += '.py'
        print(f"Running specific test: {test_file}")
        return run_specific_test(test_file)
    else:
        print("Running all tests...")
        return run_all_tests()

if __name__ == "__main__":
    sys.exit(main())

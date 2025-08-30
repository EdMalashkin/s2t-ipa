"""
Test configuration and utilities
"""

import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
TEST_LANGUAGES = ['en', 'es', 'de', 'pt']
TEST_CACHE_DIR = "test_cache"

# Sample test data that can be reused across tests
SAMPLE_TOKEN_DATA = [{
    "tokens": [
        {"text": "hello", "id": 1},
        {"text": "world", "id": 2},
        {"text": "test", "id": 3}
    ]
}]

SAMPLE_LEMMA_DATA = [{
    "tokens": [
        {"lemma": "run", "pos": "verb", "id": 1},
        {"lemma": "fast", "pos": "adverb", "id": 2},
        {"lemma": "house", "pos": "noun", "id": 3}
    ]
}]

# Test utilities
def create_mock_tsv_content():
    """Create mock TSV content for testing"""
    return """hello\t/həˈloʊ/
world\t/wɜːrld/
test\t/tɛst/
run\t/rʌn/
fast\t/fæst/
house\t/haʊs/
cat\t/kæt/
dog\t/dɔːɡ/
"""

def cleanup_test_cache():
    """Clean up test cache directory"""
    import shutil
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)

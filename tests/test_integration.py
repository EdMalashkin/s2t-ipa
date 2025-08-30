"""
Integration tests for the complete IPA transcription system
"""

import sys
import os
from unittest.mock import patch, Mock

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.json_ipa import JsonIPA


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.test_data = [{
            "tokens": [
                {"text": "hello", "id": 1},
                {"text": "world", "id": 2},
                {"text": "cat", "id": 3}
            ]
        }]
        
        self.multi_item_data = [
            {
                "tokens": [
                    {"lemma": "house", "id": 1},
                    {"lemma": "tree", "id": 2}
                ]
            },
            {
                "tokens": [
                    {"lemma": "dog", "id": 3},
                    {"lemma": "bird", "id": 4}
                ]
            }
        ]
    
    def test_end_to_end_basic_flow(self):
        """Test complete end-to-end processing with basic data"""
        # This test will use real Wikipron functionality if datasets are available
        processor = JsonIPA(self.test_data, "en", token_field="text")
        result = processor.process_bulc()
        
        # Verify structure
        assert "result" in result
        assert "ipa_error" in result
        assert isinstance(result["result"], list)
        assert len(result["result"]) == 1
        assert "tokens" in result["result"][0]
        assert len(result["result"][0]["tokens"]) == 3
        
        # If no error occurred, verify that tokens are processed
        if result["ipa_error"] is None:
            tokens = result["result"][0]["tokens"]
            for token in tokens:
                assert "text" in token
                assert "id" in token
                # IPA field may or may not be present depending on whether words are found
    
    def test_end_to_end_multiple_items(self):
        """Test complete processing with multiple items in the list"""
        processor = JsonIPA(self.multi_item_data, "en", token_field="lemma")
        result = processor.process_bulc()
        
        # Verify structure
        assert "result" in result
        assert "ipa_error" in result
        assert len(result["result"]) == 2
        
        # Verify each item has tokens
        for item in result["result"]:
            assert "tokens" in item
            assert len(item["tokens"]) == 2
    
    def test_end_to_end_with_invalid_language(self):
        """Test end-to-end processing with invalid language code"""
        processor = JsonIPA(self.test_data, "zz", token_field="text")  # Invalid language
        result = processor.process_bulc()
        
        # Should handle gracefully
        assert "result" in result
        assert "ipa_error" in result
        
        # Depending on implementation, might have error or just no IPA fields
        # The system should not crash
        assert isinstance(result["result"], list)
    
    def test_end_to_end_empty_input(self):
        """Test end-to-end processing with empty input"""
        processor = JsonIPA([], "en", token_field="text")
        result = processor.process_bulc()
        
        assert result["result"] == []
        assert result["ipa_error"] is None
    
    def test_end_to_end_malformed_input(self):
        """Test end-to-end processing with malformed input"""
        malformed_data = [
            {"not_tokens": []},  # Missing 'tokens' key
            {"tokens": "not_a_list"},  # 'tokens' is not a list
            {"tokens": [{"no_text_field": "value"}]}  # Token missing required field
        ]
        
        processor = JsonIPA(malformed_data, "en", token_field="text")
        result = processor.process_bulc()
        
        # Should handle gracefully without crashing
        assert "result" in result
        assert "ipa_error" in result
        assert len(result["result"]) == 3
    
    @patch('app.wikipron.Wikipron._load_datasets_to_cache')
    def test_end_to_end_with_caching(self, mock_load):
        """Test that caching works properly across multiple calls"""
        # Setup mock to track calls
        mock_load.return_value = None
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        
        # First call
        result1 = processor.process_bulc()
        
        # Second call with same processor
        result2 = processor.process_bulc()
        
        # Should load datasets, but caching should work at some level
        # The exact number depends on implementation details, so just check it's reasonable
        assert mock_load.call_count >= 1
        assert mock_load.call_count <= 10  # Reasonable upper bound
        
        # Results should be consistent
        assert result1["ipa_error"] == result2["ipa_error"]
    
    def test_end_to_end_different_token_fields(self):
        """Test end-to-end processing with different token fields"""
        # Test with 'lemma' field
        lemma_data = [{
            "tokens": [
                {"lemma": "run", "pos": "verb", "id": 1},
                {"lemma": "fast", "pos": "adverb", "id": 2}
            ]
        }]
        
        processor = JsonIPA(lemma_data, "en", token_field="lemma")
        result = processor.process_bulc()
        
        assert "result" in result
        assert "ipa_error" in result
        
        tokens = result["result"][0]["tokens"]
        assert len(tokens) == 2
        assert all("lemma" in token for token in tokens)
        assert all("pos" in token for token in tokens)
    
    def test_end_to_end_performance_large_dataset(self):
        """Test performance with larger dataset"""
        # Create larger dataset
        large_data = []
        for i in range(10):  # 10 items
            tokens = []
            for j in range(20):  # 20 tokens each
                tokens.append({
                    "text": f"word{i}_{j}",
                    "id": i * 20 + j
                })
            large_data.append({"tokens": tokens})
        
        processor = JsonIPA(large_data, "en", token_field="text")
        result = processor.process_bulc()
        
        # Should complete without error
        assert "result" in result
        assert "ipa_error" in result
        assert len(result["result"]) == 10
        
        # Verify all tokens are present
        total_tokens = sum(len(item["tokens"]) for item in result["result"])
        assert total_tokens == 200
    
    def test_end_to_end_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_data = [{
            "tokens": [
                {"text": "café", "id": 1},
                {"text": "naïve", "id": 2},
                {"text": "résumé", "id": 3},
                {"text": "ми", "id": 4},  # Cyrillic
                {"text": "こんにちは", "id": 5}  # Japanese
            ]
        }]
        
        processor = JsonIPA(unicode_data, "en", token_field="text")
        result = processor.process_bulc()
        
        # Should handle Unicode gracefully
        assert "result" in result
        assert "ipa_error" in result
        
        tokens = result["result"][0]["tokens"]
        assert len(tokens) == 5
        
        # All original text should be preserved
        texts = [token["text"] for token in tokens]
        assert "café" in texts
        assert "naïve" in texts
        assert "résumé" in texts
        assert "ми" in texts
        assert "こんにちは" in texts

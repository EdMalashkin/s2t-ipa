"""
Unit tests for JsonIPA class
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.json_ipa import JsonIPA
from app.wikipron import Wikipron


class TestJsonIPA:
    """Test cases for JsonIPA class functionality"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.test_data = [{
            "tokens": [
                {"text": "hello", "id": 1},
                {"text": "world", "id": 2},
                {"text": "cat", "id": 3}
            ]
        }]
        
        self.empty_data = [{
            "tokens": [
                {"text": "nonexistentword123", "id": 1},
                {"text": "anotherfakeword456", "id": 2}
            ]
        }]
    
    def test_init(self):
        """Test JsonIPA initialization"""
        processor = JsonIPA(self.test_data, "en", token_field="text")
        
        assert processor.json == self.test_data
        assert processor.lang == "en"
        assert processor.token_field == "text"
        assert isinstance(processor.wikipron, Wikipron)
        assert processor._ipa_cache == {}
    
    def test_init_default_token_field(self):
        """Test JsonIPA initialization with default token field"""
        processor = JsonIPA(self.test_data, "en")
        
        assert processor.token_field == "lemma"  # Default value
    
    @patch('app.json_ipa.Wikipron')
    def test_get_ipa_for_text_success(self, mock_wikipron_class):
        """Test _get_ipa_for_text when IPA is found"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.return_value = ("/həˈloʊ/", None)
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        result = processor._get_ipa_for_text("hello")
        
        assert result == "/həˈloʊ/"
        mock_wikipron.get_ipa.assert_called_once_with("hello")
    
    @patch('app.json_ipa.Wikipron')
    def test_get_ipa_for_text_not_found(self, mock_wikipron_class):
        """Test _get_ipa_for_text when IPA is not found"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.return_value = (None, None)
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        result = processor._get_ipa_for_text("nonexistentword")
        
        assert result == ""  # Should return empty string when not found
        mock_wikipron.get_ipa.assert_called_once_with("nonexistentword")
    
    @patch('app.json_ipa.Wikipron')
    def test_get_ipa_for_text_error(self, mock_wikipron_class):
        """Test _get_ipa_for_text when there's an error"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.return_value = (None, "Error loading dataset")
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        
        with pytest.raises(Exception, match="Error loading dataset"):
            processor._get_ipa_for_text("hello")
    
    @patch('app.json_ipa.Wikipron')
    def test_process_tokens_batch_with_ipa(self, mock_wikipron_class):
        """Test _process_tokens_batch when IPA is found"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        # Use a side_effect function that returns values based on input
        def mock_get_ipa(word):
            ipa_map = {
                "hello": ("/həˈloʊ/", None),
                "world": ("/wɜːrld/", None),
                "cat": ("/kæt/", None)
            }
            return ipa_map.get(word, (None, None))
        
        mock_wikipron.get_ipa.side_effect = mock_get_ipa
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        tokens = self.test_data[0]["tokens"].copy()  # Make a copy to avoid modifying original
        
        result = processor._process_tokens_batch(tokens, "text")
        
        assert len(result) == 3
        assert result[0]["ipa"] == "/həˈloʊ/"
        assert result[1]["ipa"] == "/wɜːrld/"
        assert result[2]["ipa"] == "/kæt/"
    
    @patch('app.json_ipa.Wikipron')
    def test_process_tokens_batch_no_ipa(self, mock_wikipron_class):
        """Test _process_tokens_batch when no IPA is found"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.return_value = (None, None)  # No IPA found
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.empty_data, "en", token_field="text")
        tokens = self.empty_data[0]["tokens"].copy()
        
        result = processor._process_tokens_batch(tokens, "text")
        
        assert len(result) == 2
        # IPA fields should not be present when no IPA found
        assert "ipa" not in result[0]
        assert "ipa" not in result[1]
    
    @patch('app.json_ipa.Wikipron')
    def test_process_tokens_batch_mixed_results(self, mock_wikipron_class):
        """Test _process_tokens_batch with mixed results (some found, some not)"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        def mock_get_ipa(word):
            if word == "hello":
                return ("/həˈloʊ/", None)
            else:
                return (None, None)
        
        mock_wikipron.get_ipa.side_effect = mock_get_ipa
        mock_wikipron_class.return_value = mock_wikipron
        
        mixed_data = [{
            "tokens": [
                {"text": "hello", "id": 1},
                {"text": "nonexistentword", "id": 2}
            ]
        }]
        
        processor = JsonIPA(mixed_data, "en", token_field="text")
        tokens = mixed_data[0]["tokens"].copy()
        
        result = processor._process_tokens_batch(tokens, "text")
        
        assert len(result) == 2
        assert result[0]["ipa"] == "/həˈloʊ/"  # Should have IPA
        assert "ipa" not in result[1]          # Should not have IPA field
    
    @patch('app.json_ipa.Wikipron')
    def test_process_bulc_success(self, mock_wikipron_class):
        """Test process_bulc successful processing"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        def mock_get_ipa(word):
            ipa_map = {
                "hello": ("/həˈloʊ/", None),
                "world": ("/wɜːrld/", None),
                "cat": ("/kæt/", None)
            }
            return ipa_map.get(word, (None, None))
        
        mock_wikipron.get_ipa.side_effect = mock_get_ipa
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        result = processor.process_bulc()
        
        assert "result" in result
        assert "ipa_error" in result
        assert result["ipa_error"] is None
        
        tokens = result["result"][0]["tokens"]
        assert tokens[0]["ipa"] == "/həˈloʊ/"
        assert tokens[1]["ipa"] == "/wɜːrld/"
        assert tokens[2]["ipa"] == "/kæt/"
    
    @patch('app.json_ipa.Wikipron')
    def test_process_bulc_error_handling(self, mock_wikipron_class):
        """Test process_bulc error handling"""
        # Mock the Wikipron instance to raise an error
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.side_effect = Exception("Test error")
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA(self.test_data, "en", token_field="text")
        result = processor.process_bulc()
        
        assert "result" in result
        assert "ipa_error" in result
        assert result["ipa_error"] is not None
        assert "Error processing IPA transcription" in result["ipa_error"]
        
        # Original data should be returned without IPA fields
        tokens = result["result"][0]["tokens"]
        for token in tokens:
            assert "ipa" not in token
    
    @patch('app.json_ipa.Wikipron')
    def test_process_bulc_non_list_input(self, mock_wikipron_class):
        """Test process_bulc with non-list input"""
        mock_wikipron = Mock()
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA("not a list", "en", token_field="text")
        result = processor.process_bulc()
        
        assert result["result"] == "not a list"
        assert result["ipa_error"] is None
    
    @patch('app.json_ipa.Wikipron')
    def test_process_bulc_empty_input(self, mock_wikipron_class):
        """Test process_bulc with empty input"""
        mock_wikipron = Mock()
        mock_wikipron_class.return_value = mock_wikipron
        
        processor = JsonIPA([], "en", token_field="text")
        result = processor.process_bulc()
        
        assert result["result"] == []
        assert result["ipa_error"] is None
    
    @patch('app.json_ipa.Wikipron')
    def test_process_bulc_invalid_structure(self, mock_wikipron_class):
        """Test process_bulc with invalid data structure"""
        mock_wikipron = Mock()
        mock_wikipron_class.return_value = mock_wikipron
        
        # Data without 'tokens' key
        invalid_data = [{"not_tokens": []}]
        
        processor = JsonIPA(invalid_data, "en", token_field="text")
        result = processor.process_bulc()
        
        assert result["result"] == invalid_data
        assert result["ipa_error"] is None
    
    @patch('app.json_ipa.Wikipron')
    def test_different_token_fields(self, mock_wikipron_class):
        """Test processing with different token fields"""
        # Mock the Wikipron instance
        mock_wikipron = Mock()
        mock_wikipron.get_ipa.return_value = ("/həˈloʊ/", None)
        mock_wikipron_class.return_value = mock_wikipron
        
        # Test with 'lemma' field
        lemma_data = [{
            "tokens": [
                {"lemma": "hello", "id": 1}
            ]
        }]
        
        processor = JsonIPA(lemma_data, "en", token_field="lemma")
        result = processor.process_bulc()
        
        assert result["result"][0]["tokens"][0]["ipa"] == "/həˈloʊ/"
        mock_wikipron.get_ipa.assert_called_with("hello")

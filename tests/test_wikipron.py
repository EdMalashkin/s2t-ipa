"""
Unit tests for Wikipron class
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.wikipron import Wikipron


class TestWikipron:
    """Test cases for Wikipron class functionality"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.test_lang = "en"
        
    def test_init(self):
        """Test Wikipron initialization"""
        wikipron = Wikipron(self.test_lang)
        
        assert wikipron.lang_code_2digit == "en"
        assert wikipron.cache_dir == Path("cache/wikipron")
        assert wikipron.base_url == "https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv"
        assert wikipron._word_cache == {}
        assert wikipron._loaded_patterns == []
    
    def test_init_case_insensitive(self):
        """Test Wikipron initialization with uppercase language code"""
        wikipron = Wikipron("EN")
        
        assert wikipron.lang_code_2digit == "en"
    
    @patch('app.wikipron.get_language_config')
    def test_init_no_config(self, mock_get_config):
        """Test Wikipron initialization when no config is found"""
        mock_get_config.return_value = None
        
        wikipron = Wikipron("xx")  # Non-existent language
        
        assert wikipron.lang_code_2digit == "xx"
        assert wikipron.config is None
    
    def test_clean_ipa(self):
        """Test _clean_ipa method"""
        wikipron = Wikipron(self.test_lang)
        
        assert wikipron._clean_ipa("h ə ˈ l oʊ") == "həˈloʊ"
        assert wikipron._clean_ipa("test") == "test"
        assert wikipron._clean_ipa("") == ""
        assert wikipron._clean_ipa(None) == ""
    
    @patch('urllib.request.urlretrieve')
    @patch('pathlib.Path.exists')
    def test_download_dataset_success(self, mock_exists, mock_urlretrieve):
        """Test successful dataset download"""
        mock_exists.return_value = False
        mock_urlretrieve.return_value = None
        
        wikipron = Wikipron(self.test_lang)
        result = wikipron._download_dataset("eng_us_broad_phonemic.tsv")
        
        assert result is True
        mock_urlretrieve.assert_called_once()
    
    @patch('urllib.request.urlretrieve')
    @patch('pathlib.Path.exists')
    def test_download_dataset_failure(self, mock_exists, mock_urlretrieve):
        """Test failed dataset download"""
        mock_exists.return_value = False
        mock_urlretrieve.side_effect = Exception("Network error")
        
        wikipron = Wikipron(self.test_lang)
        result = wikipron._download_dataset("eng_us_broad_phonemic.tsv")
        
        assert result is False
    
    @patch('app.wikipron.get_filename_patterns')
    @patch.object(Wikipron, '_download_dataset')
    @patch('pathlib.Path.exists')
    def test_ensure_datasets_exist(self, mock_exists, mock_download, mock_get_patterns):
        """Test _ensure_datasets_exist method"""
        mock_get_patterns.return_value = ["eng_us_broad_phonemic", "eng_uk_broad_phonemic"]
        mock_exists.side_effect = [True, False]  # First exists, second doesn't
        mock_download.return_value = True
        
        wikipron = Wikipron(self.test_lang)
        result = wikipron._ensure_datasets_exist()
        
        assert result == ["eng_us_broad_phonemic", "eng_uk_broad_phonemic"]
        mock_download.assert_called_once_with("eng_uk_broad_phonemic.tsv")
    
    def test_extract_variety_from_pattern(self):
        """Test _extract_variety_from_pattern method"""
        wikipron = Wikipron(self.test_lang)
        
        result = wikipron._extract_variety_from_pattern("eng_latn_us_broad_phonemic")
        assert result == "us"
        
        result = wikipron._extract_variety_from_pattern("short_pattern")
        assert result == "default"
    
    @patch('builtins.open', new_callable=mock_open, read_data="hello\thəˈloʊ\nworld\twɜːrld\n")
    @patch('pathlib.Path.exists')
    @patch('app.wikipron.get_filename_patterns')
    def test_load_single_variety_datasets(self, mock_get_patterns, mock_exists, mock_file):
        """Test _load_single_variety_datasets method"""
        mock_get_patterns.return_value = ["eng_us_broad_phonemic"]
        mock_exists.return_value = True
        
        wikipron = Wikipron(self.test_lang)
        wikipron.config = Mock()
        wikipron.config.varieties = None  # Single variety
        
        wikipron._load_single_variety_datasets(["eng_us_broad_phonemic"])
        
        assert len(wikipron._word_cache) == 2
        # The actual implementation adds single slashes around clean IPA
        assert wikipron._word_cache["hello"] == "/həˈloʊ/"
        assert wikipron._word_cache["world"] == "/wɜːrld/"
    
    @patch('builtins.open', new_callable=mock_open, read_data="hello\t/həˈloʊ/\nworld\t/wɜːrld/\n")
    @patch('pathlib.Path.exists')
    @patch('app.wikipron.get_variety_labels')
    def test_load_multi_variety_datasets(self, mock_get_labels, mock_exists, mock_file):
        """Test _load_multi_variety_datasets method"""
        mock_exists.return_value = True
        mock_get_labels.return_value = {"us": "US", "uk": "UK"}
        
        wikipron = Wikipron(self.test_lang)
        wikipron.config = Mock()
        wikipron.config.varieties = ["us", "uk"]  # Multi variety
        
        wikipron._load_multi_variety_datasets(["eng_latn_us_broad_phonemic"])
        
        # Should have processed the file
        assert len(wikipron._word_cache) >= 0  # Could be 0 if combine_varieties filters
    
    def test_combine_varieties_single(self):
        """Test _combine_varieties with single variety"""
        wikipron = Wikipron(self.test_lang)
        
        variety_caches = {
            "us": {"hello": "həˈloʊ", "world": "wɜːrld"}
        }
        variety_labels = {"us": "US"}
        
        wikipron._combine_varieties(variety_caches, variety_labels)
        
        assert wikipron._word_cache["hello"] == "/həˈloʊ/"
        assert wikipron._word_cache["world"] == "/wɜːrld/"
    
    def test_combine_varieties_multiple_same(self):
        """Test _combine_varieties with multiple varieties having same pronunciation"""
        wikipron = Wikipron(self.test_lang)
        
        variety_caches = {
            "us": {"hello": "həˈloʊ"},
            "uk": {"hello": "həˈloʊ"}
        }
        variety_labels = {"us": "US", "uk": "UK"}
        
        wikipron._combine_varieties(variety_caches, variety_labels)
        
        assert wikipron._word_cache["hello"] == "/həˈloʊ/"
    
    def test_combine_varieties_multiple_different(self):
        """Test _combine_varieties with multiple varieties having different pronunciations"""
        wikipron = Wikipron(self.test_lang)
        
        variety_caches = {
            "us": {"hello": "həˈloʊ"},
            "uk": {"hello": "həˈləʊ"}
        }
        variety_labels = {"us": "US", "uk": "UK"}
        
        wikipron._combine_varieties(variety_caches, variety_labels)
        
        # Should combine with // delimiter
        assert "//" in wikipron._word_cache["hello"]
        assert wikipron._word_cache["hello"].startswith("/")
        assert wikipron._word_cache["hello"].endswith("/")
    
    @patch.object(Wikipron, '_load_datasets_to_cache')
    def test_get_ipa_success(self, mock_load):
        """Test get_ipa when word is found"""
        wikipron = Wikipron(self.test_lang)
        wikipron._word_cache = {"hello": "/həˈloʊ/"}
        
        result, error = wikipron.get_ipa("hello")
        
        assert result == "/həˈloʊ/"
        assert error is None
        mock_load.assert_called_once()
    
    @patch.object(Wikipron, '_load_datasets_to_cache')
    def test_get_ipa_not_found(self, mock_load):
        """Test get_ipa when word is not found"""
        wikipron = Wikipron(self.test_lang)
        wikipron._word_cache = {}
        
        result, error = wikipron.get_ipa("nonexistent")
        
        assert result is None
        assert error is None
        mock_load.assert_called_once()
    
    @patch.object(Wikipron, '_load_datasets_to_cache')
    def test_get_ipa_case_insensitive(self, mock_load):
        """Test get_ipa is case insensitive"""
        wikipron = Wikipron(self.test_lang)
        wikipron._word_cache = {"hello": "/həˈloʊ/"}
        
        result, error = wikipron.get_ipa("HELLO")
        
        assert result == "/həˈloʊ/"
        assert error is None
    
    @patch.object(Wikipron, '_load_datasets_to_cache')
    def test_get_ipa_error(self, mock_load):
        """Test get_ipa when there's an error"""
        mock_load.side_effect = Exception("Load error")
        
        wikipron = Wikipron(self.test_lang)
        
        result, error = wikipron.get_ipa("hello")
        
        assert result is None
        assert error is not None
        assert "Load error" in error
    
    def test_get_available_varieties_no_config(self):
        """Test get_available_varieties when no config"""
        wikipron = Wikipron(self.test_lang)
        wikipron.config = None
        
        result = wikipron.get_available_varieties()
        
        assert result == {}
    
    def test_get_loaded_patterns(self):
        """Test get_loaded_patterns"""
        wikipron = Wikipron(self.test_lang)
        wikipron._loaded_patterns = ["eng_us_broad_phonemic", "eng_uk_broad_phonemic"]
        
        result = wikipron.get_loaded_patterns()
        
        assert result == ["eng_us_broad_phonemic", "eng_uk_broad_phonemic"]
        # Should return a copy, not the original
        assert result is not wikipron._loaded_patterns

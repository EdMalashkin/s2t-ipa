import os
import urllib.request
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from functools import lru_cache
import shutil
from .wikipron_config import get_language_config, get_filename_patterns, get_variety_labels


class Wikipron:
    def __init__(self, lang_code_2digit: str):
        """
        Initialize Wikipron with ISO 639-1 language code (2 digits)
        
        Args:
            lang_code_2digit: ISO 639-1 2-letter language code (e.g., 'en', 'da', 'de')
        """
        self.lang_code_2digit = lang_code_2digit.lower()
        
        # Get language configuration
        self.config = get_language_config(self.lang_code_2digit)
        
        if not self.config:
            print(f"Warning: No configuration found for language code '{self.lang_code_2digit}'. Using fallback.")
        
        # Configure cache directory - use mounted cache directly
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv"
        
        # Cache stores arrays of IPA varieties for each word
        self._word_cache: Dict[str, List[str]] = {}
        self._loaded_patterns: List[str] = []

    @classmethod
    def clean_all_cache(cls) -> Dict[str, any]:
        """Clean all cached files from the cache directory"""
        cache_dir = Path("cache")
        
        if not cache_dir.exists():
            return {
                "success": True,
                "message": "Cache directory does not exist",
                "files_removed": 0,
                "space_freed_bytes": 0,
                "space_freed_formatted": "0 bytes"
            }
        
        try:
            files_removed = 0
            total_size = 0
            
            # Count and remove files
            for file_path in cache_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                        files_removed += 1
                        file_path.unlink()
                    except OSError as e:
                        print(f"Warning: Could not remove {file_path}: {e}")
            
            # Remove empty subdirectories
            for dir_path in sorted(cache_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if dir_path.is_dir() and dir_path != cache_dir:
                    try:
                        dir_path.rmdir()
                    except OSError:
                        pass
            
            def format_bytes(bytes_size):
                if bytes_size == 0:
                    return "0 bytes"
                for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                    if bytes_size < 1024.0:
                        return f"{bytes_size:.1f} {unit}"
                    bytes_size /= 1024.0
                return f"{bytes_size:.1f} PB"
            
            return {
                "success": True,
                "message": "Cache files cleaned successfully",
                "files_removed": files_removed,
                "space_freed_bytes": total_size,
                "space_freed_formatted": format_bytes(total_size)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to clean cache: {str(e)}",
                "files_removed": 0,
                "space_freed_bytes": 0,
                "space_freed_formatted": "0 bytes"
            }

    def clear_memory_cache(self) -> None:
        """Clear the in-memory word cache for this instance"""
        self._word_cache.clear()
        self._loaded_patterns.clear()
    
    def _clean_ipa(self, ipa: str) -> str:
        """Remove extra spaces from IPA transcription"""
        return ipa.replace(" ", "") if ipa else ""
    
    def _download_dataset(self, filename: str) -> bool:
        """Download a specific TSV dataset file"""
        url = f"{self.base_url}/{filename}"
        local_path = self.cache_dir / filename
        
        try:
            print(f"Downloading {filename} from {url}...")
            urllib.request.urlretrieve(url, local_path)
            print(f"Successfully downloaded and cached {filename}")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False
    
    def _ensure_datasets_exist(self) -> List[str]:
        """Ensure datasets exist locally, download if needed"""
        patterns = get_filename_patterns(self.lang_code_2digit)
        available_patterns = []
        
        for pattern in patterns:
            filename = f"{pattern}.tsv"
            local_path = self.cache_dir / filename
            
            if local_path.exists() or self._download_dataset(filename):
                available_patterns.append(pattern)
                
        if not available_patterns:
            print(f"Warning: No datasets found for language code '{self.lang_code_2digit}'")
            
        return available_patterns
    
    def _load_datasets_to_cache(self) -> None:
        """Load all available datasets into memory cache"""
        if self._word_cache:  # Already loaded
            return
            
        available_patterns = self._ensure_datasets_exist()
        if not available_patterns:
            return
        
        # Collect all varieties for each word
        word_varieties = {}
        
        for pattern in available_patterns:
            filename = f"{pattern}.tsv"
            local_path = self.cache_dir / filename
            
            if not local_path.exists():
                continue
                
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or '\t' not in line:
                            continue
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            word, ipa = parts[0], parts[1]
                            clean_ipa = self._clean_ipa(ipa)
                            
                            word_key = word.lower()
                            if word_key not in word_varieties:
                                word_varieties[word_key] = []
                            
                            # Only add if this IPA variant isn't already present
                            if clean_ipa and clean_ipa not in word_varieties[word_key]:
                                word_varieties[word_key].append(clean_ipa)
                
                print(f"Loaded {filename}")
                
            except Exception as e:
                print(f"Error loading {pattern}: {e}")
        
        # Store final arrays in cache
        for word, varieties in word_varieties.items():
            self._word_cache[word] = varieties
            
        self._loaded_patterns = available_patterns
        print(f"Total words cached: {len(self._word_cache)}")
    
    def get_ipa(self, word: str) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Get IPA transcription varieties for a word
        Returns: (ipa_array, error_message)
        """
        try:
            # Load datasets to cache if not already loaded
            self._load_datasets_to_cache()
            
            # Return array of varieties or empty array
            ipa_varieties = self._word_cache.get(word.lower(), [])
            return (ipa_varieties if ipa_varieties else None, None)
        except Exception as e:
            error_msg = f"Error getting IPA for '{word}': {str(e)}"
            return (None, error_msg)
    
    def get_available_varieties(self) -> Dict[str, str]:
        """Get available varieties for this language"""
        if not self.config or not self.config.varieties:
            return {}
        return get_variety_labels(self.lang_code_2digit)
    
    def get_loaded_patterns(self) -> List[str]:
        """Get list of loaded dataset patterns"""
        return self._loaded_patterns.copy()


def get_ipa_offline(word: str, dataset_path="dan_phonemic.tsv"):
    """Legacy function for backward compatibility"""
    try:
        with open(dataset_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or '\t' not in line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    w, ipa = parts[0], parts[1]
                    if w.lower() == word.lower():
                        return ipa
    except FileNotFoundError:
        pass
    return None


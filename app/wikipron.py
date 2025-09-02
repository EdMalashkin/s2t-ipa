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
            # For unmapped languages, we'll still try to work with basic patterns
        
        # Configure cache directory - use mounted cache directly
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv"
        
        # Simple unified caching - store final formatted IPA strings
        self._word_cache: Dict[str, str] = {}
        self._loaded_patterns: List[str] = []  # Track which files we've loaded

    @classmethod
    def clean_all_cache(cls) -> Dict[str, any]:
        """
        Clean all cached files from the cache directory
        Returns: Dictionary with cleanup statistics
        """
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
            # Count files and calculate total size before deletion
            files_removed = 0
            total_size = 0
            
            for file_path in cache_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                        files_removed += 1
                    except OSError:
                        # Handle cases where file might be deleted during iteration
                        pass
            
            # Remove all cache contents
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(exist_ok=True)  # Recreate empty cache directory
            
            # Format size for human readability
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
                "message": "Cache cleaned successfully",
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
        """
        Ensure datasets exist locally, download if needed
        Returns list of available filename patterns (without .tsv extension)
        """
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
        """Load all available datasets into memory cache for fast lookups"""
        if self._word_cache:  # Already loaded
            return
            
        available_patterns = self._ensure_datasets_exist()
        if not available_patterns:
            return
            
        # Special handling for languages with multiple varieties
        if self.config and self.config.varieties and len(self.config.varieties) > 1:
            self._load_multi_variety_datasets(available_patterns)
        else:
            self._load_single_variety_datasets(available_patterns)
            
        self._loaded_patterns = available_patterns
    
    def _load_multi_variety_datasets(self, patterns: List[str]) -> None:
        """Load datasets for languages with multiple varieties (like English, Spanish, etc.)"""
        variety_caches = {}
        variety_labels = get_variety_labels(self.lang_code_2digit)
        
        # Load each variety into separate cache
        for pattern in patterns:
            filename = f"{pattern}.tsv"
            local_path = self.cache_dir / filename
            
            if not local_path.exists():
                continue
                
            variety_cache = {}
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or '\t' not in line:
                            continue
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            word, ipa = parts[0], parts[1]
                            variety_cache[word.lower()] = self._clean_ipa(ipa)
                
                # Determine variety key from pattern
                variety_key = self._extract_variety_from_pattern(pattern)
                variety_caches[variety_key] = variety_cache
                print(f"Loaded {len(variety_cache)} words from {pattern}")
                
            except Exception as e:
                print(f"Error loading {pattern}: {e}")
        
        # Combine varieties into final formatted cache
        self._combine_varieties(variety_caches, variety_labels)
    
    def _extract_variety_from_pattern(self, pattern: str) -> str:
        """Extract variety identifier from filename pattern"""
        parts = pattern.split('_')
        if len(parts) >= 4:  # iso639_3_script_variety_type
            return parts[2]
        return "default"
    
    def _combine_varieties(self, variety_caches: Dict[str, Dict[str, str]], variety_labels: Dict[str, str]) -> None:
        """Combine multiple variety caches into final formatted result"""
        all_words = set()
        for cache in variety_caches.values():
            all_words.update(cache.keys())
        
        for word in all_words:
            variety_ipas = []
            for variety_key, cache in variety_caches.items():
                ipa = cache.get(word)
                if ipa:
                    label = variety_labels.get(variety_key, variety_key)
                    variety_ipas.append((label, ipa))
            
            if variety_ipas:
                if len(variety_ipas) == 1:
                    # Single variety available
                    self._word_cache[word] = f"/{variety_ipas[0][1]}/"
                else:
                    # Multiple varieties - format as /variety1 // variety2 // variety3/
                    ipa_parts = [ipa for label, ipa in variety_ipas]
                    if len(set(ipa_parts)) == 1:
                        # All varieties have same pronunciation
                        self._word_cache[word] = f"/{ipa_parts[0]}/"
                    else:
                        # Different pronunciations
                        formatted_parts = "//".join(ipa_parts)
                        self._word_cache[word] = f"/{formatted_parts}/"
    
    def _load_single_variety_datasets(self, patterns: List[str]) -> None:
        """Load datasets for languages with single variety"""
        for pattern in patterns:
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
                            # Only add if not already present (first pattern wins)
                            if word.lower() not in self._word_cache:
                                self._word_cache[word.lower()] = f"/{clean_ipa}/"
                
                print(f"Loaded {len(self._word_cache)} words from {pattern}")
                break  # Use first available pattern
                
            except Exception as e:
                print(f"Error loading {pattern}: {e}")
    
    def get_ipa(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get IPA transcription for a word
        Returns: (ipa_result, error_message)
        """
        try:
            # Load datasets to cache if not already loaded
            self._load_datasets_to_cache()
            
            # Simple lookup - cache already contains formatted strings
            ipa_result = self._word_cache.get(word.lower())
            return (ipa_result, None)
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


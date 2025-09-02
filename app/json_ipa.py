from typing import Dict, Any, List, Optional, Tuple
import concurrent.futures
from functools import lru_cache
from .wikipron import Wikipron


class JsonIPA:
    def __init__(self, json: str, lang: str, token_field: str = "lemma"):
        self.json = json
        self.lang = lang
        self.token_field = token_field  # Field to process in tokens (default: "lemma")
        # Create one Wikipron instance at class level for the specified language
        self.wikipron = Wikipron(lang)
        # Cache for IPA lookups to avoid duplicate processing
        self._ipa_cache = {}
    
    @staticmethod
    def clean_all_cache() -> Dict[str, Any]:
        """
        Clean all cached Wikipron TSV files to free up disk space
        
        Returns: Dictionary with cleanup statistics
        """
        return Wikipron.clean_all_cache()
    
    def _get_ipa_for_text(self, text: str) -> str:
        """Get IPA transcription for any text using Wikipron"""
        # Use the class-level Wikipron instance
        ipa_result, error = self.wikipron.get_ipa(text)
        
        if error:
            # Re-raise error to be caught at the global level
            raise Exception(error)
        elif ipa_result:
            # Success - return IPA
            return ipa_result
        else:
            # Not found - return empty string
            return ""
    
    def _process_tokens_batch(self, tokens: List[Dict[str, Any]], field_name: str) -> List[Dict[str, Any]]:
        """Process a batch of tokens efficiently for any field"""
        # Extract all unique values from the specified field
        unique_values = {token[field_name] for token in tokens if field_name in token}
        
        # Batch process IPA for unique values only
        ipa_results = {}
        for value in unique_values:
            ipa_results[value] = self._get_ipa_for_text(value)
        
        # Apply IPA to all tokens, but only if IPA is not empty
        for token in tokens:
            if field_name in token:
                ipa_value = ipa_results[token[field_name]]
                if ipa_value:  # Only add IPA field if it's not empty
                    token["ipa"] = ipa_value
        
        return tokens
    
    def process_bulc(self) -> Dict[str, Any]:
        """Process JSON data and add IPA transcription to any specified field in fastest possible way"""
        try:
            if not isinstance(self.json, list):
                return {"result": self.json, "ipa_error": None}
            
            # Process each item in the list
            for item in self.json:
                if not isinstance(item, dict) or "tokens" not in item:
                    continue
                
                tokens = item["tokens"]
                if not isinstance(tokens, list):
                    continue
                
                # Process tokens in batch for maximum efficiency using the specified field
                item["tokens"] = self._process_tokens_batch(tokens, self.token_field)
            
            return {"result": self.json, "ipa_error": None}
            
        except Exception as e:
            error_msg = f"Error processing IPA transcription: {str(e)}"
            # Return original JSON without adding any IPA fields and include global error
            return {"result": self.json, "ipa_error": error_msg}

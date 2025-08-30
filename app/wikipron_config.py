"""
Wikipron Dataset Configuration
Mapping for language codes, scripts, varieties, and transcription types
Based on actual files available in https://github.com/CUNY-CL/wikipron/tree/master/data/scrape
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class LanguageVariety:
    """Configuration for a specific language variety"""
    variety: str = ""  # e.g., "uk", "us", "brazil", "portugal"
    script: str = "latn"  # Default to Latin script
    transcription_type: str = "broad"  # "broad" or "narrow"
    label: str = ""  # Human-readable label

@dataclass
class LanguageConfig:
    """Configuration for a language with all its varieties"""
    iso639_3: str
    script: str = "latn"  # Default script
    default_transcription: str = "broad"  # Default transcription type
    varieties: List[LanguageVariety] = None
    fallback_transcription: str = "narrow"  # Fallback if default not available

    def __post_init__(self):
        if self.varieties is None:
            self.varieties = []

# Comprehensive language configuration based on actual Wikipron availability
# Using ISO 639-1 (2-digit) codes as keys for easier lookup
WIKIPRON_LANGUAGE_CONFIG: Dict[str, LanguageConfig] = {
    # English - Multiple varieties with both broad transcriptions
    'en': LanguageConfig(
        iso639_3='eng',
        script='latn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('uk', 'latn', 'broad', 'UK Received Pronunciation'),
            LanguageVariety('us', 'latn', 'broad', 'US General American'),
        ]
    ),
    
    # Spanish - Multiple varieties (Spain vs Latin America)
    'es': LanguageConfig(
        iso639_3='spa',
        script='latn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('ca', 'latn', 'broad', 'Castilian Spain'),
            LanguageVariety('la', 'latn', 'broad', 'Latin America'),
        ]
    ),
    
    # Portuguese - Brazil vs Portugal
    'pt': LanguageConfig(
        iso639_3='por',
        script='latn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('bz', 'latn', 'broad', 'Brazil'),
            LanguageVariety('po', 'latn', 'broad', 'Portugal'),
        ]
    ),
    
    # Welsh - North vs South Wales
    'cy': LanguageConfig(
        iso639_3='cym',
        script='latn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('nw', 'latn', 'broad', 'North Wales'),
            LanguageVariety('sw', 'latn', 'broad', 'South Wales'),
        ]
    ),
    
    # Armenian - Eastern vs Western
    'hy': LanguageConfig(
        iso639_3='hye',
        script='armn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('e', 'armn', 'broad', 'Eastern Armenian'),
            LanguageVariety('w', 'armn', 'broad', 'Western Armenian'),
        ]
    ),
    
    # Bengali - Standard vs Dhaka variety
    'bn': LanguageConfig(
        iso639_3='ben',
        script='beng',
        default_transcription='broad',
        varieties=[
            LanguageVariety('', 'beng', 'broad', 'Standard Bengali'),
            LanguageVariety('dhaka', 'beng', 'broad', 'Dhaka'),
            LanguageVariety('rarh', 'beng', 'broad', 'Rarh Standard Bengali'),
        ]
    ),
    
    # Vietnamese - Multiple regional varieties
    'vi': LanguageConfig(
        iso639_3='vie',
        script='latn',
        default_transcription='narrow',  # Only narrow available
        varieties=[
            LanguageVariety('hanoi', 'latn', 'narrow', 'Hà Nội'),
            LanguageVariety('hue', 'latn', 'narrow', 'Huế'),
            LanguageVariety('saigon', 'latn', 'narrow', 'Saigon'),
        ]
    ),
    
    # Latin - Classical vs Ecclesiastical
    'la': LanguageConfig(
        iso639_3='lat',
        script='latn',
        default_transcription='broad',
        varieties=[
            LanguageVariety('clas', 'latn', 'broad', 'Classical'),
            LanguageVariety('eccl', 'latn', 'broad', 'Ecclesiastical'),
        ]
    ),
    
    # Languages with only broad transcription available
    'de': LanguageConfig('deu', 'latn', 'broad'),  # German
    'fr': LanguageConfig('fra', 'latn', 'broad'),  # French
    'it': LanguageConfig('ita', 'latn', 'broad'),  # Italian
    'nl': LanguageConfig('nld', 'latn', 'broad'),  # Dutch
    'pl': LanguageConfig('pol', 'latn', 'broad'),  # Polish
    'da': LanguageConfig('dan', 'latn', 'broad'),  # Danish
    'sv': LanguageConfig('swe', 'latn', 'broad'),  # Swedish
    'fi': LanguageConfig('fin', 'latn', 'broad'),  # Finnish
    'is': LanguageConfig('isl', 'latn', 'broad'),  # Icelandic
    'el': LanguageConfig('ell', 'grek', 'broad'),  # Greek
    'tr': LanguageConfig('tur', 'latn', 'broad'),  # Turkish
    'hi': LanguageConfig('hin', 'deva', 'broad'),  # Hindi
    'ar': LanguageConfig('ara', 'arab', 'broad'),  # Arabic
    'ko': LanguageConfig('kor', 'hang', 'narrow', fallback_transcription='broad'),  # Korean (only narrow)
    'ja': LanguageConfig('jpn', 'hira', 'narrow', fallback_transcription='broad'),  # Japanese (only narrow)
    'zh': LanguageConfig('zho', 'hani', 'broad'),  # Chinese
    'th': LanguageConfig('tha', 'thai', 'broad'),  # Thai
    'km': LanguageConfig('khm', 'khmr', 'broad'),  # Khmer
    'my': LanguageConfig('mya', 'mymr', 'broad'),  # Burmese
    'ka': LanguageConfig('kat', 'geor', 'broad'),  # Georgian
    'he': LanguageConfig('heb', 'hebr', 'broad'),  # Hebrew
    'sa': LanguageConfig('san', 'deva', 'broad'),  # Sanskrit
    
    # Languages with only narrow transcription available
    'ru': LanguageConfig('rus', 'cyrl', 'narrow', fallback_transcription='broad'),  # Russian
    'hu': LanguageConfig('hun', 'latn', 'narrow', fallback_transcription='broad'),  # Hungarian
    'cs': LanguageConfig('ces', 'latn', 'narrow', fallback_transcription='broad'),  # Czech
    'mk': LanguageConfig('mkd', 'cyrl', 'narrow', fallback_transcription='broad'),  # Macedonian
    'bg': LanguageConfig('bul', 'cyrl', 'narrow', fallback_transcription='broad'),  # Bulgarian
    'uk': LanguageConfig('ukr', 'cyrl', 'narrow', fallback_transcription='broad'),  # Ukrainian
    'lt': LanguageConfig('lit', 'latn', 'narrow', fallback_transcription='broad'),  # Lithuanian
    'lv': LanguageConfig('lav', 'latn', 'narrow', fallback_transcription='broad'),  # Latvian
    'fa': LanguageConfig('fas', 'arab', 'narrow', fallback_transcription='broad'),  # Persian
    
    # Languages with both broad and narrow available
    'ca': LanguageConfig('cat', 'latn', 'broad'),  # Catalan
    'eu': LanguageConfig('eus', 'latn', 'broad'),  # Basque
    'gl': LanguageConfig('glg', 'latn', 'broad'),  # Galician
    'ro': LanguageConfig('ron', 'latn', 'broad'),  # Romanian
    'sl': LanguageConfig('slv', 'latn', 'broad'),  # Slovenian
    'et': LanguageConfig('est', 'latn', 'broad'),  # Estonian
    'ga': LanguageConfig('gle', 'latn', 'broad'),  # Irish
    'gd': LanguageConfig('gla', 'latn', 'broad'),  # Scottish Gaelic
    'mt': LanguageConfig('mlt', 'latn', 'broad'),  # Maltese
    'az': LanguageConfig('aze', 'latn', 'broad'),  # Azerbaijani
    'kk': LanguageConfig('kaz', 'cyrl', 'broad'),  # Kazakh
    'tg': LanguageConfig('tgk', 'cyrl', 'broad'),  # Tajik
    'mn': LanguageConfig('mon', 'cyrl', 'broad'),  # Mongolian
    'dv': LanguageConfig('div', 'thaa', 'broad'),  # Dhivehi
    'bo': LanguageConfig('bod', 'tibt', 'broad'),  # Tibetan
    'id': LanguageConfig('ind', 'latn', 'broad'),  # Indonesian
    'ms': LanguageConfig('msa', 'latn', 'broad'),  # Malay
    'tl': LanguageConfig('tgl', 'latn', 'broad'),  # Tagalog
    'haw': LanguageConfig('haw', 'latn', 'broad'),  # Hawaiian
    'yo': LanguageConfig('yor', 'latn', 'broad'),  # Yoruba
    'ha': LanguageConfig('hau', 'latn', 'broad'),  # Hausa
    'zu': LanguageConfig('zul', 'latn', 'broad'),  # Zulu
    'af': LanguageConfig('afr', 'latn', 'broad'),  # Afrikaans
    'eo': LanguageConfig('epo', 'latn', 'broad'),  # Esperanto
    'vo': LanguageConfig('vol', 'latn', 'broad'),  # Volapük
    
    # Additional languages
    'no': LanguageConfig('nor', 'latn', 'broad'),  # Norwegian
    'sk': LanguageConfig('slk', 'latn', 'broad'),  # Slovak
    'hr': LanguageConfig('hbs', 'latn', 'broad'),    # Croatian -> use hbs Latin  
    'sr': LanguageConfig('hbs', 'cyrl', 'broad'),    # Serbian -> use hbs Cyrillic
    'bs': LanguageConfig('hbs', 'latn', 'broad'),    # Bosnian -> use hbs Latin
    'sq': LanguageConfig('sqi', 'latn', 'broad'),  # Albanian
    'be': LanguageConfig('bel', 'cyrl', 'narrow'),  # Belarusian
    'te': LanguageConfig('tel', 'telu', 'broad'),  # Telugu
    'ta': LanguageConfig('tam', 'taml', 'broad'),  # Tamil
    'ml': LanguageConfig('mal', 'mlym', 'broad'),  # Malayalam
    'kn': LanguageConfig('kan', 'knda', 'broad'),  # Kannada
    'gu': LanguageConfig('guj', 'gujr', 'broad'),  # Gujarati
    'mr': LanguageConfig('mar', 'deva', 'broad'),  # Marathi
    'ur': LanguageConfig('urd', 'arab', 'broad'),  # Urdu
    'pa': LanguageConfig('pan', 'guru', 'broad'),  # Punjabi
    'ne': LanguageConfig('nep', 'deva', 'narrow'),  # Nepali
    'si': LanguageConfig('sin', 'sinh', 'broad'),  # Sinhala
    'sw': LanguageConfig('swa', 'latn', 'broad'),  # Swahili
    'am': LanguageConfig('amh', 'ethi', 'broad'),  # Amharic
    'ky': LanguageConfig('kir', 'cyrl', 'broad'),  # Kyrgyz
    'uz': LanguageConfig('uzb', 'latn', 'broad'),  # Uzbek
    'tk': LanguageConfig('tuk', 'latn', 'broad'),  # Turkmen
    'ps': LanguageConfig('pus', 'arab', 'broad'),  # Pashto
    'lo': LanguageConfig('lao', 'laoo', 'narrow'),  # Lao
    'xh': LanguageConfig('xho', 'latn', 'narrow'),  # Xhosa
    'br': LanguageConfig('bre', 'latn', 'broad'),  # Breton
}

def get_language_config(lang_code_2digit: str) -> Optional[LanguageConfig]:
    """Get language configuration for a given ISO 639-1 (2-digit) code"""
    return WIKIPRON_LANGUAGE_CONFIG.get(lang_code_2digit.lower())

def get_filename_patterns(lang_code_2digit: str) -> List[str]:
    """
    Get all possible filename patterns for a language, in order of preference
    Returns list of patterns without .tsv extension
    """
    config = get_language_config(lang_code_2digit)
    if not config:
        # Fallback for unmapped languages - try common patterns
        # Convert 2-digit to potential 3-digit codes for fallback
        potential_3digit = _guess_iso639_3_code(lang_code_2digit)
        return [
            f"{potential_3digit}_latn_broad",
            f"{potential_3digit}_latn_narrow"
        ]
    
    patterns = []
    
    # If language has varieties, include all variety patterns
    if config.varieties:
        for variety in config.varieties:
            if variety.variety:
                patterns.append(f"{config.iso639_3}_{variety.script}_{variety.variety}_{variety.transcription_type}")
            else:
                patterns.append(f"{config.iso639_3}_{variety.script}_{variety.transcription_type}")
    else:
        # Single variety language
        patterns.append(f"{config.iso639_3}_{config.script}_{config.default_transcription}")
        
        # Add fallback if different from default
        if config.fallback_transcription != config.default_transcription:
            patterns.append(f"{config.iso639_3}_{config.script}_{config.fallback_transcription}")
    
    return patterns

def get_variety_labels(lang_code_2digit: str) -> Dict[str, str]:
    """Get variety labels for display purposes"""
    config = get_language_config(lang_code_2digit)
    if not config or not config.varieties:
        return {}
    
    labels = {}
    for variety in config.varieties:
        variety_key = variety.variety if variety.variety else "default"
        labels[variety_key] = variety.label
    
    return labels

def _guess_iso639_3_code(lang_code_2digit: str) -> str:
    """
    Simple heuristic to guess 3-digit code from 2-digit code
    This is a fallback for unmapped languages
    """
    code = lang_code_2digit.lower()
    
    # Some common mappings for fallback
    common_mappings = {
        'nb': 'nob',  # Norwegian Bokmål
        'nn': 'nno',  # Norwegian Nynorsk
        'zh': 'zho',  # Chinese
        'ja': 'jpn',  # Japanese
        'ko': 'kor',  # Korean
    }
    
    return common_mappings.get(code, code)

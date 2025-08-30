"""
WIKIPRON URL VALIDATION SUMMARY
==============================

This document summarizes the comprehensive testing of all 2-digit language URLs
built from the Wikipron repository at https://github.com/CUNY-CL/wikipron/tree/master/data/scrape

## Test Results Overview

- **Total Languages Tested**: 90
- **Languages with Working URLs**: 87 (96.7% success rate)
- **Languages with NO Working URLs**: 3 (3.3% failure rate)
- **Total URLs Tested**: 356
- **Total Successful URLs**: 145 (40.7% URL success rate)

## Success Analysis

### Excellent Coverage

Our language configuration achieves 96.7% coverage, meaning 87 out of 90 configured
2-digit language codes have at least one working Wikipron URL. This demonstrates
that our mapping from ISO 639-1 (2-digit) codes to ISO 639-3 (3-digit) codes
and the variety configurations are highly accurate.

### Multi-Variety Language Support

Several languages have excellent multi-variety support:

**English (en)**:

- UK Received Pronunciation: eng_latn_uk_broad
- US General American: eng_latn_us_broad

**Spanish (es)**:

- Castilian Spain: spa_latn_ca_broad
- Latin America: spa_latn_la_broad

**Portuguese (pt)**:

- Brazil: por_latn_bz_broad
- Portugal: por_latn_po_broad

**Vietnamese (vi)**:

- Hanoi: vie_latn_hanoi_narrow
- Huế: vie_latn_hue_narrow
- Saigon: vie_latn_saigon_narrow

**Welsh (cy)**:

- North Wales: cym_latn_nw_broad
- South Wales: cym_latn_sw_broad

**Armenian (hy)**:

- Eastern Armenian: hye_armn_e_broad
- Western Armenian: hye_armn_w_broad

**Bengali (bn)**:

- Standard: ben_beng_broad
- Dhaka: ben_beng_dhaka_broad
- Rarh Standard: ben_beng_rarh_broad

**Latin (la)**:

- Classical: lat_latn_clas_broad
- Ecclesiastical: lat_latn_eccl_broad

## Issues Identified

### Problematic Languages (3 languages with NO working URLs)

1. **Bosnian (bs)**: No working URLs found

   - Tried: bos_latn_broad, bos_latn_narrow
   - **Recommendation**: Use Serbian-Croatian (hbs) instead, which has working URLs:
     - hbs_cyrl_broad (Cyrillic)
     - hbs_latn_broad (Latin)

2. **Croatian (hr)**: No working URLs found

   - Tried: hrv_latn_broad, hrv_latn_narrow
   - **Recommendation**: Use Serbian-Croatian (hbs) instead

3. **Serbian (sr)**: No working URLs found
   - Tried: srp_cyrl_broad, srp_cyrl_narrow
   - **Recommendation**: Use Serbian-Croatian (hbs) instead

### Language Configuration Updates Needed

Based on the findings, we should update the configuration for the three problematic languages:

```python
# Remove these problematic entries:
# 'bs': LanguageConfig('bos', 'latn', 'broad'),  # Bosnian
# 'hr': LanguageConfig('hrv', 'latn', 'broad'),  # Croatian
# 'sr': LanguageConfig('srp', 'cyrl', 'broad'),  # Serbian

# Replace with unified Serbo-Croatian:
'bs': LanguageConfig('hbs', 'latn', 'broad'),    # Bosnian -> use hbs Latin
'hr': LanguageConfig('hbs', 'latn', 'broad'),    # Croatian -> use hbs Latin
'sr': LanguageConfig('hbs', 'cyrl', 'broad'),    # Serbian -> use hbs Cyrillic
```

## Key Findings

### Stress Markers Not Available

- **Finding**: All stress-marked variants (URLs ending with `_stress.tsv`) returned 404 errors
- **Impact**: The 40.7% URL success rate is because we tested both normal and stress variants
- **Recommendation**: Remove stress variant testing since they're not available

### Script and Transcription Accuracy

- **Finding**: Our script and transcription type mappings are highly accurate
- **Examples of correct mappings**:
  - Greek: ell_grek_broad ✓
  - Arabic: ara_arab_broad ✓
  - Georgian: kat_geor_broad ✓
  - Thai: tha_thai_broad ✓
  - Khmer: khm_khmr_broad ✓

### Broad vs Narrow Transcription Patterns

- **Most languages** have broad transcription available
- **Some languages** (Russian, Hungarian, Czech, etc.) only have narrow transcription
- **Our fallback system** correctly handles these cases

## Recommendations

### 1. Update Language Configuration

Apply the Serbo-Croatian fixes for bs/hr/sr languages.

### 2. Remove Stress Testing

Remove stress variant URL generation since these files don't exist.

### 3. Add More Language Mappings

Consider adding more 2-digit language codes based on available 3-digit codes in Wikipron.

### 4. Implement Automatic Validation

Set up periodic testing to validate URL availability as Wikipron dataset updates.

## Files Generated

1. **wikipron_comprehensive_test_results.json**: Complete test results with all details
2. **working_wikipron_urls.txt**: Clean list of all working URLs by language
3. **test_all_wikipron_urls.py**: Test script for ongoing validation

## Conclusion

The comprehensive URL validation confirms that our Wikipron integration is highly successful
with 96.7% language coverage. The main issue is with South Slavic languages (Bosnian,
Croatian, Serbian) which can be resolved by using the unified Serbo-Croatian (hbs) language
code that Wikipron provides.

Our multi-variety language support is working excellently, providing users with regional
pronunciation variants for English, Spanish, Portuguese, Vietnamese, Welsh, Armenian,
Bengali, and Latin.

The system is ready for production use with the minor configuration updates recommended above.
"""

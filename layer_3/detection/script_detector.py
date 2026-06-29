class Scripts:
    """Centralized script constants to prevent string typos across Layer 3."""
    DEVANAGARI = "devanagari"
    ARABIC = "arabic"
    CYRILLIC = "cyrillic"
    HANGUL = "hangul"
    CJK = "cjk"
    LATIN = "latin"
    UNKNOWN = "unknown"


class UnicodeRanges:
    """Named Unicode ranges for maintainability and scalability."""
    DEVANAGARI_START, DEVANAGARI_END = 0x0900, 0x097F
    ARABIC_START, ARABIC_END = 0x0600, 0x06FF
    CYRILLIC_START, CYRILLIC_END = 0x0400, 0x04FF
    HANGUL_START, HANGUL_END = 0xAC00, 0xD7AF
    CJK_START, CJK_END = 0x4E00, 0x9FFF
    
    # Latin and skip-ranges
    LATIN_UPPER_START, LATIN_UPPER_END = 0x0041, 0x005A
    LATIN_LOWER_START, LATIN_LOWER_END = 0x0061, 0x007A
    LATIN_EXT_START, LATIN_EXT_END = 0x00C0, 0x024F


class ScriptDetector:
    """
    Layer 1 of the Language Detection Engine.
    Provides microsecond-speed script identification using Unicode ranges.
    """

    def detect_script(self, text: str) -> str:
        """
        Scans text for identifying non-Latin characters.
        Returns the script name (e.g., Scripts.DEVANAGARI), or Scripts.UNKNOWN.
        """
        if not text or not text.strip():
            return Scripts.UNKNOWN

        has_latin = False

        for char in text:
           
            if not char.isalpha():
                continue

            cp = ord(char)

        
            if UnicodeRanges.DEVANAGARI_START <= cp <= UnicodeRanges.DEVANAGARI_END:
                return Scripts.DEVANAGARI
            
           
            if UnicodeRanges.ARABIC_START <= cp <= UnicodeRanges.ARABIC_END:
                return Scripts.ARABIC
            
           
            if UnicodeRanges.CYRILLIC_START <= cp <= UnicodeRanges.CYRILLIC_END:
                return Scripts.CYRILLIC
            
         
            if UnicodeRanges.HANGUL_START <= cp <= UnicodeRanges.HANGUL_END:
                return Scripts.HANGUL
            
            # TODO: Future enhancement: 
            # distinguish Chinese vs Japanese using Hiragana/Katakana detection.
            # (e.g., HIRAGANA: 0x3040-0x309F, KATAKANA: 0x30A0-0x30FF)
            # CJK (Chinese, Japanese Kanji)
            if UnicodeRanges.CJK_START <= cp <= UnicodeRanges.CJK_END:
                return Scripts.CJK

            
            if (UnicodeRanges.LATIN_UPPER_START <= cp <= UnicodeRanges.LATIN_UPPER_END) or \
               (UnicodeRanges.LATIN_LOWER_START <= cp <= UnicodeRanges.LATIN_LOWER_END) or \
               (UnicodeRanges.LATIN_EXT_START <= cp <= UnicodeRanges.LATIN_EXT_END):
                has_latin = True

       
        if has_latin:
            return Scripts.LATIN

        return Scripts.UNKNOWN
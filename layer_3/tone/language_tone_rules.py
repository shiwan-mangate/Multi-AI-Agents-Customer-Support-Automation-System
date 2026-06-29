"""
Configuration file for cultural communication preferences.
Maps ISO language codes to their expected baseline formality and style.
Used by the ToneAdjustmentService to combine agent persona with cultural expectations.
"""

LANGUAGE_TONE_RULES = {
    "en": {
        "formality": "neutral",
        "style": "direct"
    },
    "hi": {
        "formality": "respectful",
        "style": "professional"
    },
    "es": {
        "formality": "friendly",
        "style": "conversational"
    },
    "fr": {
        "formality": "formal",
        "style": "professional"
    },
    "de": {
        "formality": "formal",
        "style": "precise"
    },
    "ar": {
        "formality": "formal",
        "style": "respectful"
    }
}
## layer_0/language.py
from langdetect import detect_langs, DetectorFactory
import langid

DetectorFactory.seed = 0

ALLOWED_LANGUAGES = {"en", "hi", "es", "fr", "de", "ar"}
def detect_language(message: str) -> str:

    if not message or len(message.strip()) < 3:
        return "en"

    message = " ".join(message.strip().split())

    message_lower = message.lower()

    words = set(message_lower.split())

    strong_markers = {
        "mujhe", "chahiye", "kardo", "karne",
        "nhi", "nahi", "kya", "rha",
        "raha", "gaya", "gye", "aapka",
        "kise", "kaise"
    }

    common_markers = {
        "hai", "toh", "aur", "tha", "ko",
        "ne", "me", "kar", "ho", "kab",
        "mera", "meri", "mere", "tune",
        "maine", "karo"
    }

    if (
        words.intersection(strong_markers)
        or len(words.intersection(common_markers)) >= 2
    ):
        return "hi"

    try:

        lang_id_result, lang_id_score = langid.classify(message)
        detect_results = detect_langs(message)
        top_lang = detect_results[0].lang
        top_prob = detect_results[0].prob
        all_markers = strong_markers.union(common_markers)

        if (
            (lang_id_result == "sw" or top_lang == "sw")
            and words.intersection(all_markers)
        ):
            return "hi"

        if lang_id_result == top_lang and lang_id_result in ALLOWED_LANGUAGES:
            return lang_id_result

        if top_prob > 0.85 and top_lang in ALLOWED_LANGUAGES:
            return top_lang
            
        if lang_id_result in ALLOWED_LANGUAGES:
            return lang_id_result

        return 'en'

    except Exception:
        return "en"
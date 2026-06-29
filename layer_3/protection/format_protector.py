import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class FormatProtector:
    PATTERNS = {
        "CODE_BLOCK": re.compile(r'```[\s\S]*?```'),
        "INLINE_CODE": re.compile(r'`[^`]+`'),
        "LINK": re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        "BOLD": re.compile(r'\*\*[^*]+\*\*'),
        "ITALIC": re.compile(r'\*[^*]+\*'),
        "LIST": re.compile(r'^(?:\s*[-*+]|\s*\d+\.)\s+.+$', re.MULTILINE),
        "HTML": re.compile(r'<[^>]+>')
    }

    def protect_formats(self, text: str) -> Tuple[str, Dict[str, str]]:
        if not text:
            return "", {}

        protected_text = text
        format_map: Dict[str, str] = {}
        counters: Dict[str, int] = {}

        for format_type, pattern in self.PATTERNS.items():
            matches = list(pattern.finditer(protected_text))
            for match in reversed(matches):
                match_str = match.group(0)
                
                if format_type not in counters:
                    counters[format_type] = 1
                else:
                    counters[format_type] += 1
                
                
                placeholder = f"__FMT_{format_type}_{counters[format_type]}__"
                
                format_map[placeholder] = match_str
                protected_text = (
                    protected_text[:match.start()] + 
                    placeholder + 
                    protected_text[match.end():]
                )

        logger.info(f"Format Protection | Count={len(format_map)}")
        return protected_text, format_map

    def restore_formats(self, text: str, format_map: Dict[str, str]) -> str:
        if not text or not format_map:
            return text

        restored_text = text
        sorted_placeholders = sorted(format_map.keys(), key=len, reverse=True)
        
        for placeholder in sorted_placeholders:
            original_value = format_map[placeholder]
            if placeholder not in restored_text:
                logger.warning(f"Translation anomaly: Format placeholder {placeholder} dropped.")
                continue
            restored_text = re.sub(re.escape(placeholder), original_value, restored_text)

        return restored_text
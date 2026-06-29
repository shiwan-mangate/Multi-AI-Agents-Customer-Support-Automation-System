# layer_4_analytics/integrations/translation_mapper.py

from typing import Dict, List, Any


class TranslationMapper:
    """
    Anti-Corruption Layer (ACL) for Layer 3 Translation records.
    Normalizes language ISO codes and strict boolean success states for the LanguageAnalyticsService.
    Contains zero business logic or metric calculations.
    """

    UNKNOWN_LANGUAGE = "unknown"

    TRUE_VALUES = {True, 1, "1", "true", "True", "TRUE", "t", "T", "yes", "Yes", "Y"}
    FALSE_VALUES = {False, 0, "0", "false", "False", "FALSE", "f", "F", "no", "No", "N"}

    @staticmethod
    def map_translation_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a single raw translation database record into a clean analytical format.
        """

        raw_ticket = row.get("ticket_id")
        raw_lang = row.get("language_code")
        raw_success = row.get("translation_success")

        if raw_lang is not None:
            language_code = str(raw_lang).lower().strip()
        else:
            language_code = TranslationMapper.UNKNOWN_LANGUAGE

        if raw_success in TranslationMapper.TRUE_VALUES:
            translation_success = True
        elif raw_success in TranslationMapper.FALSE_VALUES:
            translation_success = False
        else:
            translation_success = False

        return {
            "ticket_id": str(raw_ticket) if raw_ticket is not None else None,
            "language_code": language_code,
            "translation_success": translation_success,
        }

    @classmethod
    def map_translation_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bulk maps a list of raw translation database dictionaries.
        """
        return [cls.map_translation_row(row) for row in rows]
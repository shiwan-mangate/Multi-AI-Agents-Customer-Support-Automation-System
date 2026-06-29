import logging
from typing import Dict, Any

from layer_3.tone.agent_tone_rules import AGENT_TONE_RULES
from layer_3.tone.language_tone_rules import LANGUAGE_TONE_RULES

logger = logging.getLogger(__name__)

class ToneAdjustmentService:
    """
    Applies agent-specific and language-specific tone adjustments
    before outbound translation. Compounds multiple tone elements 
    (apologies, empathy, formality) into a cohesive prefix.
    """

    def adjust_tone(
        self,
        response_text: str,
        source_agent: str,
        target_language: str
    ) -> str:

        if not response_text or not source_agent:
            return response_text

        # 1. Fetch Rules & Log Unknowns
        agent_rule = AGENT_TONE_RULES.get(source_agent)
        if not agent_rule:
            logger.warning(f"ToneAdjustmentService | Unknown source agent: {source_agent}")
            agent_rule = {}

        language_rule = LANGUAGE_TONE_RULES.get(target_language, {})

        # 2. Build Prefix
        prefix = self._build_prefix(
            agent_rule=agent_rule,
            language_rule=language_rule
        )

        if not prefix:
            return response_text

        adjusted_response = f"{prefix}{response_text}"

        logger.info(
            f"ToneAdjustmentService | Applied Tone | "
            f"Agent={source_agent} | Language={target_language}"
        )

        return adjusted_response

    def _build_prefix(
        self,
        agent_rule: Dict[str, Any],
        language_rule: Dict[str, Any]
    ) -> str:
        
        prefix_parts = []

        # 1. Apology Check
        if agent_rule.get("apology"):
            prefix_parts.append("We sincerely apologize for the inconvenience.")

        # 2. Empathy Check
        if agent_rule.get("empathy"):
            prefix_parts.append("We completely understand your concern and are here to help.")

        # 3. Base Tone Check
        tone = agent_rule.get("tone")
        if tone == "friendly":
            prefix_parts.append("We are glad to connect with you!")
        elif tone == "professional" and not agent_rule.get("empathy"):
            prefix_parts.append("We would like to share an update regarding your request.")
        elif tone == "helpful":
            prefix_parts.append("For your assistance, here is the information you need:")

        # 4. Formality Check (Agent + Target Language Rules combined)
        agent_formality = agent_rule.get("formality", "neutral")
        lang_formality = language_rule.get("formality", "neutral")

        if lang_formality == "formal" or agent_formality == "formal":
            # If no other prefixes triggered, provide a formal bridge
            if not prefix_parts:
                prefix_parts.append("Please be advised:")

        # 5. Join and return
        if not prefix_parts:
            return ""

        return " ".join(prefix_parts) + " "

    def get_tone_metadata(
        self,
        source_agent: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Returns the computed tone metadata for Layer 4 telemetry and analytics tracking.
        """
        agent_rule = AGENT_TONE_RULES.get(source_agent, {})
        language_rule = LANGUAGE_TONE_RULES.get(target_language, {})

        return {
            "agent": source_agent,
            "language": target_language,
            "tone": agent_rule.get("tone", "neutral"),
            "agent_formality": agent_rule.get("formality", "neutral"),
            "language_formality": language_rule.get("formality", "neutral"),
            "requires_apology": agent_rule.get("apology", False),
            "requires_empathy": agent_rule.get("empathy", False)
        }
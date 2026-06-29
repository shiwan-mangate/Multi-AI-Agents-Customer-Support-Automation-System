import re
import logging
from typing import Dict, Any, List, Tuple

from layer_2_escalation_agent.schemas.trigger_assessment import (
    TriggerAssessment,
    TriggerCategory,
    TriggerReason,
)

logger = logging.getLogger(__name__)


class TriggerEngine:
    """
    Deterministic escalation trigger classification engine.
    """

    # Aligned key lookup paths cleanly
    PRIORITY_MAP = {
        TriggerCategory.LEGAL: 1,
        TriggerCategory.SECURITY: 2,
        TriggerCategory.SLA: 3,
        TriggerCategory.MANUAL_REVIEW: 4,
        TriggerCategory.CHURN: 5,
        TriggerCategory.REPEAT_ISSUE: 6,
        TriggerCategory.KNOWLEDGE_GAP: 7,
        TriggerCategory.OPERATIONAL: 8,
        TriggerCategory.GENERAL: 9,
    }

    def __init__(self):
        self.legal_pattern = re.compile(
            r"\b(lawyer|legal|court|sue|lawsuit|consumer forum|legal notice)\b",
            re.IGNORECASE,
        )

        # Refactored: Fixed missing line breaks and string concatenation boundary traps
        self.security_pattern = re.compile(
            r"\b("
            r"unauthorized login|"
            r"hacked|"
            r"stolen card|"
            r"fraud|"
            r"fraud transaction|"
            r"identity theft|"
            r"breach|"
            r"account compromised"
            r")\b",
            re.IGNORECASE,
        )

        self.sla_pattern = re.compile(
            r"\b("
            r"overdue|"
            r"waiting for days|"
            r"no response|"
            r"unacceptable delay|"
            r"still waiting|"
            r"nobody responded"
            r")\b",
            re.IGNORECASE,
        )

        self.operational_pattern = re.compile(
            r"\b("
            r"system down|"
            r"service unavailable|"
            r"payment failed|"
            r"gateway timeout|"
            r"technical outage|"
            r"dependency failure|"
            r"server error"
            r")\b",
            re.IGNORECASE,
        )

        self.repeat_issue_threshold = 2

    def assess(
        self,
        message: str,
        sentiment: str,
        source_agent: str,
        workflow_logs: List[Dict[str, Any]],
        knowledge_gap_detected: bool = False,
        repeat_issue_count: int = 0,
    ) -> TriggerAssessment:

        normalized_message = (message or "").strip()
        normalized_sentiment = (sentiment or "").strip().lower()
        normalized_source = (source_agent or "system").strip().lower()

        detected_triggers: List[Tuple[TriggerCategory, TriggerReason]] = []

        detected_triggers.extend(self._detect_legal(normalized_message))
        detected_triggers.extend(self._detect_security(normalized_message))
        detected_triggers.extend(self._detect_sla(normalized_message))
        detected_triggers.extend(self._detect_operational(normalized_message))
        detected_triggers.extend(self._detect_churn(normalized_sentiment))
        detected_triggers.extend(self._detect_manual_review(workflow_logs))
        detected_triggers.extend(self._detect_repeat_issue(repeat_issue_count))
        detected_triggers.extend(
            self._detect_knowledge_gap(knowledge_gap_detected)
        )

        primary_category, all_reasons = self._resolve_priority(
            detected_triggers,
            normalized_source,
        )

        # Refactored: Returned values extract standard lowercase text primitives 
        # to guarantee safe schema translation and downstream processing
        return TriggerAssessment(
            category=primary_category.value if hasattr(primary_category, "value") else str(primary_category),
            reasons=[r.value if hasattr(r, "value") else str(r) for r in all_reasons],
            duplicate_case_detected=False,
            existing_case_id=None,
        )

    def _detect_legal(
        self,
        message: str
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        matches = set(self.legal_pattern.findall(message))
        return [
            (TriggerCategory.LEGAL, TriggerReason.LEGAL_LANGUAGE)
            for _ in matches
        ]

    def _detect_security(
        self,
        message: str
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        matches = set(self.security_pattern.findall(message))
        triggers = []

        for match in matches:
            if "fraud" in match.lower():
                triggers.append(
                    (TriggerCategory.SECURITY, TriggerReason.FRAUD_SUSPICION)
                )
            else:
                triggers.append(
                    (TriggerCategory.SECURITY, TriggerReason.TAKEOVER_SUSPICION)
                )

        return triggers

    def _detect_sla(
        self,
        message: str
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        matches = set(self.sla_pattern.findall(message))
        return [
            (TriggerCategory.SLA, TriggerReason.SLA_BREACH_IMMINENT)
            for _ in matches
        ]

    def _detect_operational(
        self,
        message: str
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        matches = set(self.operational_pattern.findall(message))
        return [
            (TriggerCategory.OPERATIONAL, TriggerReason.POLICY_CONFLICT)
            for _ in matches
        ]

    def _detect_churn(
        self,
        sentiment: str
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        # FIX: Mapped to strict allowable sentiment ENUMS defined in tickets.sql
        if sentiment in {"angry"}:
            return [
                (TriggerCategory.CHURN, TriggerReason.HOSTILE_LANGUAGE)
            ]

        if sentiment in {"frustrated"}:
            return [
                (TriggerCategory.CHURN, TriggerReason.CHURN_THREAT)
            ]

        return []

    def _detect_manual_review(
        self,
        workflow_logs: List[Dict[str, Any]]
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        triggers = []

        for log in workflow_logs:
            message = str(log.get("message", "")).lower()

            if "identity verification failed" in message:
                triggers.append(
                    (
                        TriggerCategory.MANUAL_REVIEW,
                        TriggerReason.IDENTITY_VERIFICATION_FAILED,
                    )
                )

            elif (
                "manual review required" in message
                or "human review required" in message
                or "specialist escalation required" in message
            ):
                triggers.append(
                    (
                        TriggerCategory.MANUAL_REVIEW,
                        TriggerReason.LOW_CONFIDENCE,
                    )
                )

        return triggers

    def _detect_repeat_issue(
        self,
        repeat_issue_count: int
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        if repeat_issue_count >= self.repeat_issue_threshold:
            return [
                (
                    TriggerCategory.REPEAT_ISSUE,
                    TriggerReason.REPEAT_ISSUE_DETECTED,
                )
            ]
        return []

    def _detect_knowledge_gap(
        self,
        knowledge_gap_detected: bool
    ) -> List[Tuple[TriggerCategory, TriggerReason]]:
        if knowledge_gap_detected:
            return [
                (
                    TriggerCategory.KNOWLEDGE_GAP,
                    TriggerReason.KNOWLEDGE_GAP_DETECTED,
                )
            ]
        return []

    def _resolve_priority(
        self,
        detected_triggers,
        source_agent: str,
    ):
        if not detected_triggers:
            return (
                TriggerCategory.GENERAL,
                [TriggerReason.LOW_CONFIDENCE],
            )

        # Handle priority mapping comparisons safely across types
        sorted_triggers = sorted(
            detected_triggers,
            key=lambda item: self.PRIORITY_MAP.get(item[0], 99),
        )

        primary_category = sorted_triggers[0][0]

        unique_reasons = []
        seen = set()

        for _, reason in sorted_triggers:
            if reason not in seen:
                unique_reasons.append(reason)
                seen.add(reason)

        return primary_category, unique_reasons
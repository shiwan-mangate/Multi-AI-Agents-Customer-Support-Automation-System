import logging
from datetime import datetime, timedelta, UTC

from layer_2_escalation_agent.schemas.risk_assessment import RiskAssessment
from layer_2_escalation_agent.schemas.trigger_assessment import TriggerAssessment
from layer_2_escalation_agent.schemas.customer_context import CustomerContext
from layer_2_escalation_agent.schemas.routing_decision import RoutingDecision

logger = logging.getLogger(__name__)


class RoutingService:
    """
    Deterministic escalation routing policy engine.
    """

    CATEGORY_TEAM_MAP = {
        "legal": "legal_response_team",
        "security": "security_incident_response",
        "sla": "customer_resolution_team",
        "churn": "retention_team",
        "repeat_issue": "customer_resolution_team",
        "knowledge_gap": "support_specialist_team",
        "operational": "technical_incident_team",
        "general": "general_support_team",
    }

    MANUAL_REVIEW_TEAM_MAP = {
        "refund_agent": "billing_operations_team",
        "account_agent": "account_security_team",
        "faq_agent": "support_specialist_team",
    }

    def decide(
        self,
        trigger_assessment: TriggerAssessment,
        risk_assessment: RiskAssessment,
        customer_context: CustomerContext,
        source_agent: str,
    ) -> RoutingDecision:
        """
        Resolve operational ownership + SLA deadline.
        """

        category = trigger_assessment.category.value.lower() if hasattr(trigger_assessment.category, "value") else str(trigger_assessment.category).lower()
        
        # Refactored: Capture clean lowercase string value to align with RiskEngine changes
        risk_level = risk_assessment.level.value.lower() if hasattr(risk_assessment.level, "value") else str(risk_assessment.level).lower()
        
        customer_tier = (
            customer_context.customer_tier.value
            if hasattr(customer_context.customer_tier, "value")
            else str(customer_context.customer_tier or "standard")
        ).strip().lower()

        normalized_source_agent = (
            source_agent or "system"
        ).strip().lower()

        assigned_team = self._resolve_team(
            category,
            normalized_source_agent,
        )

        sla_deadline = self._resolve_sla_deadline(
            risk_level,
            customer_tier,
        )

        routing_reason = (
            f"Escalation routed via '{category}' policy "
            f"from source agent '{normalized_source_agent}'."
        )

        # Refactored: String matching performs lowercase lookup natively
        requires_immediate_attention = (risk_level == "urgent")

        logger.info(
            "Routing complete | team=%s | risk=%s | tier=%s | deadline=%s",
            assigned_team,
            risk_level,
            customer_tier,
            sla_deadline.isoformat(),
        )

        return RoutingDecision(
            assigned_team=assigned_team,
            target_queue=assigned_team,
            # Pass risk_level directly; the Config block on RoutingDecision 
            # resolves it cleanly back to the internal field alias name
            risk_level=risk_level,
            sla_deadline=sla_deadline,
            routing_reason=routing_reason,
            requires_immediate_attention=requires_immediate_attention,
        )

    def _resolve_team(
        self,
        category: str,
        source_agent: str,
    ) -> str:
        """
        Resolve operational queue ownership.
        """
        if category == "manual_review":
            return self._resolve_manual_review_team(source_agent)

        return self.CATEGORY_TEAM_MAP.get(
            category,
            "general_support_team",
        )

    def _resolve_manual_review_team(
        self,
        source_agent: str,
    ) -> str:
        """
        Manual-review ownership routing.
        """
        return self.MANUAL_REVIEW_TEAM_MAP.get(
            source_agent,
            "general_support_team",
        )

    def _resolve_sla_deadline(
        self,
        risk_level: str, # Refactored: Explicit string processing
        customer_tier: str,
    ) -> datetime:
        """
        Resolve absolute SLA deadline.
        """
        now = datetime.now(UTC)

        if risk_level == "urgent":
            return now + timedelta(minutes=30)

        # Refactored: Dictionary tokens updated to lowercase to ensure matching alignment
        base_sla_hours = {
            "high": 4.0,
            "medium": 8.0,
            "low": 24.0,
        }.get(risk_level, 24.0)

        final_hours = self._apply_vip_sla_override(
            base_sla_hours,
            customer_tier,
        )

        return now + timedelta(hours=final_hours)

    def _apply_vip_sla_override(
        self,
        base_hours: float,
        customer_tier: str,
    ) -> float:
        """
        Commercial SLA acceleration.
        """
        if customer_tier == "enterprise":
            return base_hours * 0.5

        if customer_tier == "premium":
            return base_hours * 0.75

        return base_hours
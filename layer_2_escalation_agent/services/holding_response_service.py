import logging
from typing import Optional
from layer_2_escalation_agent.schemas.risk_assessment import RiskAssessment
from layer_2_escalation_agent.schemas.routing_decision import RoutingDecision
from layer_2_escalation_agent.schemas.trigger_assessment import TriggerAssessment
from layer_2_escalation_agent.schemas.customer_context import CustomerContext

logger = logging.getLogger(__name__)


class HoldingResponseService:
    """
    Service layer responsible for selecting and rendering customer-facing holding templates.
    """

    # FIXED HERE: Added proper 'self' instance reference to definition signature
    def _select_template(
        self,
        category: str,
        risk_level: str,
        customer_tier: str,
    ) -> str:
        """
        Select template based on core triage factors.
        """
        category = category.lower()
        risk_level = risk_level.lower()
        customer_tier = customer_tier.lower()

        if risk_level == "urgent":
            return (
                "Our senior engineering and operations teams are actively reviewing your case. "
                "We expect to provide a direct update within 30 minutes."
            )
    
        if category == "security":
            return (
                "Your security concern is our highest priority. This case has been routed to our "
                "Incident Response Team for immediate validation."
            )

        if customer_tier in {"enterprise", "premium"}:
            return (
                f"As a VIP account partner, your escalation has been prioritized for accelerated "
                f"handling. A representative will contact you shortly."
            )

        return (
            "Your request has been successfully escalated to our specialized support engineering queue. "
            "We are gathering diagnostics and will follow up with you as soon as possible."
        )

    def generate(
        self,
        risk_assessment: RiskAssessment,
        routing_decision: RoutingDecision,
        trigger_assessment: TriggerAssessment,
        customer_context: CustomerContext,
        channel: str = "chat",
    ) -> str:
        """
        Generate public-facing message.
        """
        category = trigger_assessment.category.value if hasattr(trigger_assessment.category, "value") else str(trigger_assessment.category)
        risk_level = risk_assessment.level.value if hasattr(risk_assessment.level, "value") else str(risk_assessment.level)
        customer_tier = customer_context.customer_tier.value if hasattr(customer_context.customer_tier, "value") else str(customer_context.customer_tier)

        try:
            # FIXED HERE: Invoked cleanly as an instance method execution
            return self._select_template(
                category=category,
                risk_level=risk_level,
                customer_tier=customer_tier,
            )
        except Exception as exc:
            logger.error("Template selection failed internally: %s", str(exc))
            raise exc
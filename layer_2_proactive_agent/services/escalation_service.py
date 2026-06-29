from datetime import datetime, UTC
from crm_agent.schemas.customer_profile import CustomerProfile
from layer_2_proactive_agent.schemas.signal_assessment import SignalAssessment
from layer_2_proactive_agent.schemas.risk_assessment import RiskAssessment
from layer_2_proactive_agent.schemas.escalation_handoff import EscalationHandoff
from layer_2_proactive_agent.schemas.enums import RiskLevel
from layer_2_proactive_agent.utils.logger import logger


class EscalationService:
    """
    Creates escalation handoff contracts for downstream 
    Escalation Agent workflows (Layer 3).
    """

    URGENCY_MAPPING = {
        RiskLevel.LOW: "low",
        RiskLevel.MEDIUM: "medium",
        RiskLevel.HIGH: "high",
        RiskLevel.URGENT: "urgent", 
    }

    def handoff(
        self,
        workflow_id: str,
        customer_profile: CustomerProfile,
        signal_assessment: SignalAssessment,
        risk_assessment: RiskAssessment,
    ) -> EscalationHandoff:
        """
        Build EscalationHandoff contract.

        The proactive workflow already owns the workflow_id, 
        so we derive a deterministic string-based escalation 
        ticket_id from it to conform to the database schema.
        """
        ticket_id = f"ESC-{workflow_id}"

        logger.info(
            "Status=START | Operation=ESCALATION_HANDOFF | Workflow=%s | Customer=%s",
            workflow_id,
            customer_profile.customer_id,
        )

        # Directly grab last_sentiment from the flat model root to align with database column schema
        sentiment = getattr(customer_profile, "last_sentiment", None) or "unknown"

        # Safely get the mapped urgency string, defaulting to "medium" if unknown
        urgency = self.URGENCY_MAPPING.get(risk_assessment.risk_level, "medium")

        # Safely extract churn score (handles both nested Pydantic or flat DB mock structures)
        churn_score = 0
        if hasattr(customer_profile, "churn_intelligence") and customer_profile.churn_intelligence:
            churn_score = getattr(customer_profile.churn_intelligence, "churn_score", 0)
        else:
            churn_score = getattr(customer_profile, "churn_score", 0)

        # Enriched LLM / Supervisor context payload
        escalation_message = f"""
PROACTIVE RETENTION ESCALATION

Trigger Category:
{signal_assessment.signal_type.value}

Customer Tier:
{customer_profile.tier}

Churn Score:
{churn_score}

Risk Level:
{risk_assessment.risk_level.value}

Risk Score:
{risk_assessment.risk_score}

Risk Reasons:
{chr(10).join(f"- {reason}" for reason in risk_assessment.risk_reasons)}

Negative Ticket Count:
{getattr(customer_profile, 'negative_ticket_count', 0)}

Escalation Candidate:
{risk_assessment.escalation_candidate}
""".strip()

        handoff = EscalationHandoff(
            ticket_id=ticket_id,
            customer_id=customer_profile.customer_id,
            customer_email=customer_profile.customer_email,
            source_agent="proactive_agent",
            initial_intent=signal_assessment.signal_type.value,
            initial_sentiment=sentiment,
            initial_urgency=urgency,
            supervisor_confidence=1.0,
            message_raw=escalation_message,
            message_english=escalation_message,
            
            repeat_issue_count=getattr(customer_profile, "negative_ticket_count", 0),
            knowledge_gap_detected=False,
            
            created_at=datetime.now(UTC),
        )

        logger.info(
            "Status=SUCCESS | Operation=ESCALATION_HANDOFF | Workflow=%s | Ticket=%s",
            workflow_id,
            ticket_id,
        )

        return handoff
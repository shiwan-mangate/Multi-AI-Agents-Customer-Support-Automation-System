from datetime import datetime, UTC
from typing import Any, Dict

from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository
from layer_2_proactive_agent.database.session import SessionLocal
from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.utils.logger import logger
from crm_agent.schemas.customer_profile import (
    CustomerProfile,
    SentimentProfile,
    ChurnMetrics,
)


def customer_context_node(state: ProactiveState) -> Dict[str, Any]:
    """
    Loads customer intelligence from CRM database and enriches workflow state.
    
    Verified against flat DB schema:
    - Automatically maps flat columns like last_sentiment and churn_score 
      into nested Pydantic schemas.
    """
    workflow_id = state["workflow_id"]
    signal = state["signal"]
    customer_id = signal.customer_id

    logger.info(
        "Status=START | Node=CUSTOMER_CONTEXT | Workflow=%s | Customer=%s",
        workflow_id,
        customer_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    if customer_id <= 0:
        raise ValueError(f"Invalid customer_id: {customer_id}")

    # Use a secure context manager instead of raw instantiation to ensure connection safety
    try:
        with SessionLocal() as db:
            repo = CustomerProfileRepository(session=db)
            orm_profile = repo.get_profile(customer_id)
            
            if orm_profile is None:
                raise ValueError(f"Customer profile not found: {customer_id}")
            
            # ==========================================
            # 🟢 FIX: Defensive Tier Sanitization
            # ==========================================
            raw_tier = getattr(orm_profile, "tier", "standard")
            if raw_tier == "premium_plus":
                safe_tier = "premium"
            elif raw_tier not in ["standard", "premium", "enterprise"]:
                logger.warning(
                    "Unknown tier '%s' detected for Customer %s. Defaulting to 'standard'.",
                    raw_tier, customer_id
                )
                safe_tier = "standard"
            else:
                safe_tier = raw_tier

            # Map the flat table row columns into structured Pydantic schemas safely
            customer_profile = CustomerProfile(
                customer_id=orm_profile.customer_id,
                customer_email=orm_profile.customer_email,
                tier=safe_tier,  # <--- FIXED: Now safely sanitized!
                ltv=orm_profile.ltv,

                total_tickets=orm_profile.total_tickets,
                total_faq_tickets=orm_profile.total_faq_tickets,
                total_refund_tickets=orm_profile.total_refund_tickets,
                total_account_tickets=orm_profile.total_account_tickets,

                total_escalations=orm_profile.total_escalations,
                total_denials=orm_profile.total_denials,
                total_failures=orm_profile.total_failures,
                total_clarifications=orm_profile.total_clarifications,
                total_duplicate_suppressions=orm_profile.total_duplicate_suppressions,

                repeat_negative_count=orm_profile.repeat_negative_count,
                repeat_escalation_count=orm_profile.repeat_escalation_count,
                duplicate_request_count=orm_profile.duplicate_request_count,
                negative_ticket_count=orm_profile.negative_ticket_count,

                sentiment_profile=SentimentProfile(
                    last_sentiment=getattr(orm_profile, "last_sentiment", None) or "neutral",
                    sentiment_history=getattr(orm_profile, "sentiment_history", []) or [],
                    negative_sentiment_count=orm_profile.negative_ticket_count,
                ),

                churn_intelligence=ChurnMetrics(
                    churn_score=getattr(orm_profile, "churn_score", 0),
                    churn_level=str(
                        getattr(orm_profile, "churn_risk_level", 
                        getattr(orm_profile, "churn_level", "low"))
                    ).lower(),
                    churn_last_updated=(
                        getattr(orm_profile, "churn_last_updated", None) or datetime.now(UTC)
                    ),
                ),

                issue_tags=getattr(orm_profile, "issue_frequency", {}) or {},
                agent_interactions=getattr(orm_profile, "agent_interaction_frequency", {}) or {},

                languages_used=getattr(orm_profile, "languages_used", []) or [],
                preferred_language=getattr(orm_profile, "preferred_language", "en"),

                first_seen_at=orm_profile.first_seen_at,
                last_ticket_at=orm_profile.last_ticket_at,
                updated_at=orm_profile.updated_at,
            )

        logger.info(
            "Status=SUCCESS | Node=CUSTOMER_CONTEXT | Workflow=%s",
            workflow_id,
        )

        return {
            "customer_profile": customer_profile,
            "current_node": "customer_context_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "customer_context_node",
                    "message": f"Customer profile loaded for customer_id={customer_id}",
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Status=FAILED | Node=CUSTOMER_CONTEXT | Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )
        raise
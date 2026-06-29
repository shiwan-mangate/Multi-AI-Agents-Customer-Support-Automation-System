import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.customer_context import CustomerContext
from layer_2_escalation_agent.repositories.customer_repository import CustomerRepository
from layer_2_escalation_agent.repositories.ticket_repository import TicketRepository
from layer_2_escalation_agent.db.session import get_db

logger = logging.getLogger(__name__)


def _normalize_customer_tier(
    subscription_plan: str | None,
    profile_tier: str | None,
) -> str:
    raw_value = subscription_plan or profile_tier or "standard"
    normalized = str(raw_value).strip().lower()

    if "enterprise" in normalized:
        return "enterprise"

    if "premium" in normalized or "pro" in normalized:
        return "premium"

    return "standard"


def customer_context_node(
    state: EscalationState,
    customer_repo=None,
    ticket_repo=None
) -> EscalationState:
    """
    Hydrate escalation workflow with customer business intelligence.
    """
    logger.info("Executing customer_context_node")

    state["current_node"] = "customer_context_node"

    customer_id = state["customer_id"]
    initial_intent = state.get("initial_intent")

    profile = {}
    subscription = {}
    risk_profile = {}

    tier = "standard"
    ltv = 0.0
    total_past_tickets = 0
    total_past_escalations = 0
    open_escalations = 0
    resolved_escalations = 0
    repeat_issue_count = 0
    historical_sentiment = "neutral"
    
    negative_feedback_count = 0
    unresolved_ticket_count = 0
    churn_score = 0.0
    subscription_status = "active"

    session = None
    db_generator = None

    try:
        if customer_repo is not None and ticket_repo is not None:
            c_repo = customer_repo
            t_repo = ticket_repo
        else:
            db_generator = get_db()
            session = next(db_generator)
            c_repo = CustomerRepository(session)
            t_repo = TicketRepository(session)

        profile = c_repo.get_customer_by_id(customer_id) or {}
        subscription = c_repo.get_customer_subscription(customer_id) or {}
        risk_profile = c_repo.get_customer_risk_profile(customer_id) or {}

        tier = _normalize_customer_tier(
            subscription_plan=subscription.get("plan_name"),
            profile_tier=profile.get("account_tier"),
        )

        try:
            ltv = float(profile.get("total_spent", 0.0))
        except (TypeError, ValueError):
            ltv = 0.0

        escalation_history = c_repo.get_escalation_history(
            customer_id,
            limit=100,
        )
        total_past_escalations = len(escalation_history)

        for esc in escalation_history:
            status = str(esc.get("status", "unknown")).strip().lower()
            if status in ["open", "pending", "in_progress", "escalated", "new"]:
                open_escalations += 1
            else:
                resolved_escalations += 1

        # =========================================================
        # 🟢 LAYER 0 PARITY: Ensure ticket counts perfectly match CRM
        # =========================================================
        if hasattr(t_repo, "get_previous_ticket_count"):
            total_past_tickets = t_repo.get_previous_ticket_count(customer_id)
        else:
            # Absolute fallback if the method wasn't updated
            recent_tickets = t_repo.get_recent_tickets(customer_id, limit=100)
            total_past_tickets = len(recent_tickets)

        # Bug #1 Fixed: Positional argument satisfied by the updated repository
        raw_repeat_count = t_repo.count_repeat_issues(customer_id=customer_id)
        repeat_issue_count = max(raw_repeat_count - 1, 0)

        last_sentiment = t_repo.get_last_ticket_sentiment(customer_id)

        if last_sentiment:
            normalized_sent = str(last_sentiment).strip().lower()

            sentiment_map = {
                "calm": "neutral",
                "happy": "positive",
                "satisfied": "positive",
                "upset": "frustrated",
                "frustrated": "frustrated",
                "frustration": "frustrated",
                "mad": "angry",
                "furious": "angry",
                "angry": "angry",
                "neutral": "neutral",
                "positive": "positive",
                "mixed": "neutral",
            }
            historical_sentiment = sentiment_map.get(normalized_sent, "neutral")

        negative_feedback_count = int(
            risk_profile.get("negative_feedback_count") 
            or risk_profile.get("negative_ticket_count") 
            or 0
        )

        unresolved_ticket_count = int(
            risk_profile.get("total_failures") or 0
        )

        churn_score = float(
            risk_profile.get("churn_score") or 0.0
        )

        subscription_status = (
            subscription.get("status") or "active"
        )

        logger.info(
            "Customer context hydrated | customer_id=%s | tier=%s | ltv=%.2f | churn_score=%.2f | total_tickets=%s",
            customer_id,
            tier,
            ltv,
            churn_score,
            total_past_tickets
        )

    except Exception as exc:
        # Fail-closed handling: Stop the workflow if hydration fails
        logger.exception(
            "CRITICAL: Customer context hydration failed | customer_id=%s",
            customer_id
        )
        raise  

    finally:
        if session:
            session.close()
        if db_generator:
            try:
                next(db_generator)
            except StopIteration:
                pass

    customer_context = CustomerContext(
        customer_id=customer_id,
        customer_name=profile.get("name", "Unknown Customer"),
        customer_email=profile.get("email", state.get("customer_email", "")),
        customer_tier=tier,
        ltv=ltv,
        total_past_tickets=total_past_tickets,  # 🟢 Perfectly aligned with Layer 0 CRM
        total_past_escalations=total_past_escalations,
        open_escalations=open_escalations,
        resolved_escalations=resolved_escalations,
        repeat_issue_count=repeat_issue_count,
        historical_sentiment_trend=historical_sentiment,
        negative_feedback_count=negative_feedback_count,
        unresolved_ticket_count=unresolved_ticket_count,
        subscription_status=subscription_status,
        churn_score=churn_score
    )

    state["customer_context"] = customer_context

    log_entry = {
        "node": "customer_context_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Customer business context assembled.",
        "data": {
            "customer_id": customer_id,
            "tier": tier,
            "ltv": ltv,
            "total_past_tickets": total_past_tickets,
            "total_past_escalations": total_past_escalations,
            "open_escalations": open_escalations,
            "resolved_escalations": resolved_escalations,
            "repeat_issue_count": repeat_issue_count,
            "historical_sentiment": historical_sentiment,
            "churn_score": churn_score,
            "negative_feedback_count": negative_feedback_count,
            "unresolved_ticket_count": unresolved_ticket_count,
            "subscription_status": subscription_status
        },
    }

    state["workflow_logs"].append(log_entry)

    return state
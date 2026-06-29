from datetime import datetime, UTC
from decimal import Decimal
from typing import Optional

# FIX: Imported Integer for casting JSON text back to math-able numbers
from sqlalchemy import select, update, func, cast, Integer
# FIX: Imported array to define the JSONB target paths
from sqlalchemy.dialects.postgresql import insert, JSONB, array
from sqlalchemy.orm import Session

from crm_agent.db.models.customer_profile_model import CustomerProfile
from crm_agent.schemas.crm_event import CRMResolvedEvent


class CustomerProfileRepository:
    """
    Atomic CRM customer memory repository.
    """

    def __init__(self, session: Session):
        self.session = session

    def upsert_profile_from_event(self, event: CRMResolvedEvent) -> None:
        now = datetime.now(UTC)

        customer_id = event.customer.customer_id
        customer_email = event.customer.customer_email
        tier = event.customer.tier
        print("DEBUG LTV:", event.customer.customer_id, event.customer.ltv)
        ltv = event.customer.ltv or Decimal("0.00")

        intent = event.analytics.intent if event.analytics else "unknown"
        sentiment = event.analytics.sentiment_end if event.analytics else "neutral"
        source_agent = event.event.source_agent
        status = event.resolution.status

        is_negative = 1 if sentiment in ["frustrated", "angry"] else 0
        is_escalation = 1 if status == "escalated" else 0
        is_denial = 1 if status == "denied" else 0
        is_failure = 1 if status == "failed" else 0
        is_clarification = 1 if status == "clarification_required" else 0
        is_duplicate = 1 if status == "duplicate_suppressed" else 0

        faq_inc = 1 if source_agent == "faq_agent" else 0
        refund_inc = 1 if source_agent == "refund_agent" else 0
        account_inc = 1 if source_agent == "account_agent" else 0

        stmt = insert(CustomerProfile).values(
            customer_id=customer_id,
            customer_email=customer_email,
            tier=tier,
            ltv=ltv,
            total_tickets=1,
            total_faq_tickets=faq_inc,
            total_refund_tickets=refund_inc,
            total_account_tickets=account_inc,
            total_escalations=is_escalation,
            total_denials=is_denial,
            total_failures=is_failure,
            total_clarifications=is_clarification,
            total_duplicate_suppressions=is_duplicate,
            negative_ticket_count=is_negative,
            last_sentiment=sentiment,
            sentiment_history=[sentiment],
            issue_frequency={intent: 1},
            agent_interaction_frequency={source_agent: 1},
            first_seen_at=now,
            last_ticket_at=now,
            updated_at=now,
            created_at=now,
        )

        # ---------------------------------------------------------
        # FIX: Atomic JSONB Increment Logic
        # ---------------------------------------------------------
        # 1. Safely extract existing JSONB or initialize empty dict
        base_issue_freq = func.coalesce(CustomerProfile.issue_frequency, cast({}, JSONB))
        base_agent_freq = func.coalesce(CustomerProfile.agent_interaction_frequency, cast({}, JSONB))

        # 2. Extract specific keys as text, cast to Integer (default to 0), and add 1
        new_issue_count = func.coalesce(base_issue_freq[intent].astext.cast(Integer), 0) + 1
        new_agent_count = func.coalesce(base_agent_freq[source_agent].astext.cast(Integer), 0) + 1

        # 3. Use PostgreSQL jsonb_set to insert the mathematically incremented value
        issue_freq_update = func.jsonb_set(
            base_issue_freq,
            array([intent]),
            func.to_jsonb(new_issue_count)
        )
        agent_freq_update = func.jsonb_set(
            base_agent_freq,
            array([source_agent]),
            func.to_jsonb(new_agent_count)
        )

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["customer_id"],
            set_={
                "customer_email": customer_email,
                "tier": tier,
                "ltv": ltv,

                "total_tickets": CustomerProfile.total_tickets + 1,
                "total_faq_tickets": CustomerProfile.total_faq_tickets + faq_inc,
                "total_refund_tickets": CustomerProfile.total_refund_tickets + refund_inc,
                "total_account_tickets": CustomerProfile.total_account_tickets + account_inc,
                "total_escalations": CustomerProfile.total_escalations + is_escalation,
                "total_denials": CustomerProfile.total_denials + is_denial,
                "total_failures": CustomerProfile.total_failures + is_failure,
                "total_clarifications": CustomerProfile.total_clarifications + is_clarification,
                "total_duplicate_suppressions": CustomerProfile.total_duplicate_suppressions + is_duplicate,
                "negative_ticket_count": CustomerProfile.negative_ticket_count + is_negative,

                "last_sentiment": sentiment,
                "sentiment_history": func.array_append(
                    CustomerProfile.sentiment_history,
                    sentiment
                ),

                # Map directly to the safe atomic JSONB calculation expressions
                "issue_frequency": issue_freq_update,
                "agent_interaction_frequency": agent_freq_update,

                "last_ticket_at": now,
                "updated_at": now,
            }
        )

        self.session.execute(upsert_stmt)
        

    def get_profile(self, customer_id: int) -> Optional[CustomerProfile]:
        stmt = select(CustomerProfile).where(
            CustomerProfile.customer_id == customer_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def update_churn_state(
        self,
        customer_id: int,
        new_score: Decimal,  # Aligned type definition with database table structure numeric parameters
        new_level: str
    ) -> None:
        stmt = (
            update(CustomerProfile)
            .where(CustomerProfile.customer_id == customer_id)
            .values(
                churn_score=new_score,
                churn_level=new_level,
                churn_last_updated=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

        self.session.execute(stmt)
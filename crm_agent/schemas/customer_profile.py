from datetime import datetime, UTC
from decimal import Decimal
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class SentimentProfile(BaseModel):
    last_sentiment: Optional[str] = None

    sentiment_history: List[str] = Field(
        default_factory=list,
        description="Rolling limited history"
    )

    negative_sentiment_count: int = 0


class ChurnMetrics(BaseModel):
    churn_score: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2
    )

    churn_level: Literal[
        "low",
        "medium",
        "high",
        "urgent"
    ] = "low"

    churn_last_updated: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class CustomerProfile(BaseModel):
    """
    Persistent CRM customer intelligence profile.
    Updated atomically via PostgreSQL UPSERT.
    """

    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    customer_email: Optional[EmailStr] = None

    tier: Literal[
        "standard",
        "premium",
        "enterprise"
    ] = "standard"

    ltv: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2
    )

    total_tickets: int = 0
    total_faq_tickets: int = 0
    total_refund_tickets: int = 0
    total_account_tickets: int = 0
    total_escalations: int = 0
    total_denials: int = 0
    total_failures: int = 0
    total_clarifications: int = 0
    total_duplicate_suppressions: int = 0

    repeat_negative_count: int = 0
    repeat_escalation_count: int = 0
    duplicate_request_count: int = 0
    negative_ticket_count: int = 0

    sentiment_profile: SentimentProfile = Field(
        default_factory=SentimentProfile
    )

    churn_intelligence: ChurnMetrics = Field(
        default_factory=ChurnMetrics
    )

    # Reconciled names to align with customer_support_profiles database jsonb schemas
    issue_frequency: Dict[str, int] = Field(default_factory=dict)
    agent_interaction_frequency: Dict[str, int] = Field(default_factory=dict)

    languages_used: List[str] = Field(default_factory=list)
    preferred_language: str = "en"

    first_seen_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    last_ticket_at: Optional[datetime] = None

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    # =========================================================================
    # Backwards-Compatible Properties for Existing Logic
    # =========================================================================
    @property
    def issue_tags(self) -> Dict[str, int]:
        """Redirects existing references to issue_tags back to issue_frequency."""
        return self.issue_frequency

    @issue_tags.setter
    def issue_tags(self, value: Dict[str, int]) -> None:
        self.issue_frequency = value

    @property
    def agent_interactions(self) -> Dict[str, int]:
        """Redirects existing references to agent_interactions back to agent_interaction_frequency."""
        return self.agent_interaction_frequency

    @agent_interactions.setter
    def agent_interactions(self, value: Dict[str, int]) -> None:
        self.agent_interaction_frequency = value
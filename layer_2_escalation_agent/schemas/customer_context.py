from enum import Enum
from pydantic import BaseModel, Field

class CustomerTier(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SentimentTrend(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"

class CustomerContext(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str
    customer_tier: CustomerTier = Field(default=CustomerTier.STANDARD)
    ltv: float = Field(default=0.0, ge=0.0, description="Customer lifetime value in dollars.")
    total_past_tickets: int = Field(default=0, ge=0)
    total_past_escalations: int = Field(default=0, ge=0)
    repeat_escalation_count: int = 0
    # 🟢 FIX 9: Added discrete escalation counters
    open_escalations: int = Field(default=0, ge=0)
    resolved_escalations: int = Field(default=0, ge=0)
    
    repeat_issue_count: int = Field(default=0, ge=0, description="Number of repeated issue reports in same category.")
    historical_sentiment_trend: SentimentTrend = Field(default=SentimentTrend.NEUTRAL, description="Rolling sentiment trend from historical tickets.")
    
    # Enhanced Risk Intelligence Fields
    negative_feedback_count: int = Field(default=0, ge=0, description="Total negative ratings from past interactions.")
    unresolved_ticket_count: int = Field(default=0, ge=0, description="Number of currently open or unresolved tickets.")
    subscription_status: str = Field(default="active", description="Current status of the customer's subscription.")
    churn_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Propensity to churn (0.0 to 100.0).")
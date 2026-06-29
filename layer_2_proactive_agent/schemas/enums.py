from enum import Enum


class SignalType(str, Enum):
    """Supported proactive detection signals."""

    INACTIVE_CUSTOMER = "INACTIVE_CUSTOMER"
    HIGH_CHURN_RISK = "HIGH_CHURN_RISK"
    RECENT_NEGATIVE_EXPERIENCE = "RECENT_NEGATIVE_EXPERIENCE"
    VIP_RETENTION_RISK = "VIP_RETENTION_RISK"


class RiskLevel(str, Enum):
    """Risk severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OutreachAction(str, Enum):
    """Decision outcomes from proactive evaluation."""

    NO_ACTION = "NO_ACTION"
    OUTREACH = "OUTREACH"
    ESCALATE = "ESCALATE"


class SignalSource(str, Enum):
    """Origin of the proactive signal."""

    CRM = "CRM"
    STRIPE = "STRIPE"
    SHOPIFY = "SHOPIFY"
    STATUS_PAGE = "STATUS_PAGE"
    SYSTEM = "SYSTEM"


class OutreachStatus(str, Enum):
    """Final workflow status."""

    OUTREACH_CREATED = "OUTREACH_CREATED"
    SUPPRESSED = "SUPPRESSED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    NO_ACTION = "NO_ACTION"


__all__ = [
    "SignalType",
    "RiskLevel",
    "OutreachAction",
    "SignalSource",
    "OutreachStatus",
]
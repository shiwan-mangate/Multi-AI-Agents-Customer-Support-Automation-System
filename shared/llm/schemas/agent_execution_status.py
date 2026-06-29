from enum import Enum


class AgentExecutionStatus(str, Enum):
    RESOLVED = "RESOLVED"

    PENDING_HUMAN = "PENDING_HUMAN"
    PENDING_CUSTOMER = "PENDING_CUSTOMER"

    ESCALATED = "ESCALATED"

    FAILED = "FAILED"
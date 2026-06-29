from datetime import datetime, UTC
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)

from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
)
from layer_2_proactive_agent.schemas.signal_assessment import (
    SignalAssessment,
)
from layer_2_proactive_agent.schemas.risk_assessment import (
    RiskAssessment,
)
from layer_2_proactive_agent.schemas.outreach_decision import (
    OutreachDecision,
)
from layer_2_proactive_agent.schemas.outreach_message import (
    OutreachMessage,
)
from layer_2_proactive_agent.schemas.escalation_handoff import (
    EscalationHandoff,
)


class ProactiveOutput(BaseModel):
    """
    Public output contract of the Proactive Agent (Layer 2).

    Returned by response_node and consumed by:
    - CRM Agent
    - Integration tests
    - End-to-end workflows
    - Future orchestration layers

    Verified against DB constraints:
    - workflow_id -> character varying (str)
    - customer_id -> bigint (int)
    """

    model_config = ConfigDict(
        frozen=True
    )

    workflow_id: str = Field(
        ...,
        description="Unique workflow identifier matching DB varchar type."
    )

    agent_id: str = Field(
        default="proactive_agent",
        description="Agent producing this output."
    )

    status: OutreachStatus = Field(
        ...,
        description="Final workflow status."
    )

    customer_id: int = Field(
        ...,
        description="Customer identifier matching DB bigint type."
    )

    signal_assessment: Optional[SignalAssessment] = Field(
        default=None,
        description=(
            "Signal interpretation produced "
            "by signal_analysis_node. "
            "None if suppressed early."
        )
    )

    risk_assessment: Optional[RiskAssessment] = Field(
        default=None,
        description=(
            "Final business risk assessment. "
            "None if suppressed early."
        )
    )

    decision: Optional[OutreachDecision] = Field(
        default=None,
        description=(
            "Final orchestration decision. "
            "None if suppressed early."
        )
    )

    outreach_message: Optional[OutreachMessage] = Field(
        default=None,
        description=(
            "Generated outreach message. "
            "Present only when status=OUTREACH_CREATED."
        )
    )

    escalation_handoff: Optional[EscalationHandoff] = Field(
        default=None,
        description=(
            "Escalation payload. "
            "Present only when status=ESCALATION_REQUIRED."
        )
    )

    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Workflow completion timestamp."
    )
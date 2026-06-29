from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    RiskLevel,
)


class SignalAssessment(BaseModel):
    """
    Output produced by signal_analysis_node.
    Converts a raw Signal into an interpreted
    business assessment used by downstream
    risk scoring and decision nodes.
    """
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "signal_type": "HIGH_CHURN_RISK",
                "severity": "HIGH",
                "detected_reason": (
                    "Customer churn score exceeded threshold."
                ),
                "requires_immediate_attention": True,
            }
        }
    )
    signal_type: SignalType = Field(..., description="Signal category being analyzed." )
    severity: RiskLevel = Field(..., description="Business severity assigned to the signal." )
    detected_reason: str = Field(...,description="Human-readable explanation of why the signal was triggered.")
    requires_immediate_attention: bool = Field(
        default=False,
        description=(
            "Indicates whether immediate action should be considered."
        )
    )
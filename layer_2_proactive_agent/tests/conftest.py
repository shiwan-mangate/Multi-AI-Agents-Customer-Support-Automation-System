import pytest
from decimal import Decimal

from layer_2_proactive_agent.schemas.signal import (
    Signal,
)

# Fix 1: Corrected CRM schema import
from crm_agent.schemas.customer_profile import (
    CustomerProfile,
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

from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    SignalSource,
    RiskLevel,
    OutreachAction,
)


@pytest.fixture
def sample_signal():
    """Base signal indicating a high churn risk from CRM."""
    return Signal(
        signal_id="SIG-001",
        customer_id=123,
        signal_type=SignalType.HIGH_CHURN_RISK,
        signal_source=SignalSource.CRM,
        signal_context={
            "churn_score": 85
        },
    )


@pytest.fixture
def sample_customer_profile():
    """Standard customer profile mapping to the sample signal."""
    return CustomerProfile(
        customer_id=123,
        customer_email="test@example.com",
        tier="standard",
        ltv=Decimal("500.00"),
    )


@pytest.fixture
def sample_signal_assessment():
    """Post-analysis assessment of the base signal."""
    return SignalAssessment(
        signal_type=
            SignalType.HIGH_CHURN_RISK,
            
        severity=
            RiskLevel.HIGH,
            
        detected_reason=
            "Customer churn score exceeded threshold.",
            
        requires_immediate_attention=
            True,
    )


@pytest.fixture
def sample_risk_assessment():
    """Computed business risk combining signal and profile."""
    # Fix 3: Added missing risk_reasons list
    return RiskAssessment(
        risk_level=
            RiskLevel.HIGH,
            
        risk_score=
            Decimal("85.00"),
            
        risk_reasons=[
            "Customer churn score exceeded threshold."
        ],
        
        escalation_candidate=
            False,
    )


@pytest.fixture
def escalation_risk_assessment():
    """High-severity risk assessment requiring escalation."""
    # Fix 6: Added escalation risk fixture
    return RiskAssessment(
        risk_level=
            RiskLevel.CRITICAL,
            
        risk_score=
            Decimal("98.00"),
            
        risk_reasons=[
            "Critical churn risk detected alongside high LTV."
        ],
        
        escalation_candidate=
            True,
    )


@pytest.fixture
def sample_outreach_decision():
    """Final autonomous decision to contact the customer."""
    # Fix 2: Removed hallucinated confidence field
    return OutreachDecision(
        action=
            OutreachAction.OUTREACH,
            
        reason=
            "Customer exhibits elevated churn risk.",
            
        review_required=
            False,
    )


@pytest.fixture
def sample_outreach_message():
    """The generated payload for external communication."""
    return OutreachMessage(
        subject=
            "Checking In",
            
        body=
            "Hello customer...",
            
        channel=
            "email",
            
        generated_by=
            "test-model",
    )


@pytest.fixture
def sample_proactive_state(
    sample_signal,
    sample_customer_profile,
    sample_signal_assessment,
    sample_risk_assessment,
    sample_outreach_decision,
    sample_outreach_message,
) -> ProactiveState:
    """
    Fully hydrated LangGraph state dictionary.
    Used for testing downstream nodes without executing upstream nodes.
    """
    # Fix 4: Added ProactiveState return typing
    return {
        "workflow_id": 
            "WF-001",
            
        "signal_id": 
            "SIG-001",
            
        "status": 
            "ACTIVE",
            
        "signal": 
            sample_signal,
            
        "customer_profile":
            sample_customer_profile,
            
        "signal_assessment":
            sample_signal_assessment,
            
        "risk_assessment":
            sample_risk_assessment,
            
        "decision":
            sample_outreach_decision,
            
        "outreach_message":
            sample_outreach_message,
            
        "escalation_handoff":
            None,
            
        "crm_event":
            None,
            
        "output":
            None,
            
        "suppressed":
            False,
            
        "suppression_reason":
            None,
            
        "current_node":
            None,
            
        "workflow_logs":
            [],
            
        "errors":
            [],
    }


@pytest.fixture
def suppressed_state(
    sample_proactive_state,
) -> ProactiveState:
    """
    State representing a workflow that has been suppressed early.
    """
    # Fix 5: Added suppressed state fixture
    state = sample_proactive_state.copy()
    
    state["suppressed"] = True
    state["suppression_reason"] = "Customer already contacted within 30 days."
    
    return state
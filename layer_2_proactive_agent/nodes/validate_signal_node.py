from datetime import datetime, UTC
from typing import Dict, Any

from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.schemas.enums import SignalType
from layer_2_proactive_agent.utils.logger import logger


REQUIRED_SIGNAL_CONTEXT = {
    SignalType.HIGH_CHURN_RISK: [
        "churn_score"
    ],
    SignalType.INACTIVE_CUSTOMER: [
        "days_inactive"
    ],
    SignalType.RECENT_NEGATIVE_EXPERIENCE: [
        "negative_interactions"
    ],
    SignalType.VIP_RETENTION_RISK: [
        "churn_score",
        "ltv",
    ],
}

def validate_signal_node(state: ProactiveState) -> Dict[str, Any]:
    """
    Gatekeeper node. 
    Ensures the graph fails fast if the input signal is structurally malformed,
    missing required business context, or contains null values.
    """
    workflow_id = state.get("workflow_id", "UNKNOWN")
    logger.info(
        "Status=START | Node=VALIDATE_SIGNAL | Workflow=%s",
        workflow_id,
    )
    timestamp = datetime.now(UTC).isoformat()
    signal = state.get("signal")
    
    try:
        # 1. Structural Validation
        if not signal:
            raise ValueError("Missing 'signal' payload in state.")
        if not signal.signal_id or not str(signal.signal_id).strip():
            raise ValueError("Signal missing valid 'signal_id'.")
        
        # Ensures customer_id is a valid integer (matching DB bigint requirements)
        if not isinstance(signal.customer_id, int) or signal.customer_id <= 0:
            raise ValueError(f"Invalid customer_id: {signal.customer_id}")
            
        if not isinstance(signal.signal_type, SignalType):
            raise ValueError(f"Unsupported signal_type: {signal.signal_type}")
        
        # 2. Business Logic Validation
        signal_context = signal.signal_context or {}
        required_fields = REQUIRED_SIGNAL_CONTEXT.get(signal.signal_type, [])
        
        # Validate that the key exists AND the value is not None
        missing = [
            field for field in required_fields
            if field not in signal_context or signal_context[field] is None
        ]
        
        if missing:
            raise ValueError(
                f"Missing or null required signal_context fields for {signal.signal_type.name}: "
                f"{', '.join(missing)}"
            )

        logger.info(
            "Status=SUCCESS | Node=VALIDATE_SIGNAL | Workflow=%s | SignalID=%s",
            workflow_id,
            signal.signal_id,
        )

        return {
            "current_node": "validate_signal_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "validate_signal_node",
                    "message": f"Signal {signal.signal_id} validated successfully (Structure & Business Rules).",
                }
            ]
        }
        
    except ValueError as e:
        error_msg = str(e)
        logger.error(
            "Status=FAILED | Node=VALIDATE_SIGNAL | Workflow=%s | Error=%s", 
            workflow_id, 
            error_msg
        )
        raise ValueError(f"State Validation Failed: {error_msg}")
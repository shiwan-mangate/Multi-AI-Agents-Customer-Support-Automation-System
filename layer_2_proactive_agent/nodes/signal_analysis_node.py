from datetime import datetime, UTC
from typing import Dict, Any
from layer_2_proactive_agent.services.signal_detection_service import (SignalDetectionService,)
from layer_2_proactive_agent.utils.logger import (logger,)
from layer_2_proactive_agent.schemas.proactive_state import (ProactiveState,)
signal_detection_service = SignalDetectionService()


def signal_analysis_node(
    state: ProactiveState,
) -> Dict[str, Any]:
    """
    Converts incoming signals into
    business-level assessments.
    """

    workflow_id = state["workflow_id"]
    signal = state["signal"]

    logger.info(
        "Status=START | "
        "Node=SIGNAL_ANALYSIS | "
        "Workflow=%s | "
        "SignalId=%s | "
        "SignalType=%s",
        workflow_id,
        signal.signal_id,
        signal.signal_type.value,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:

        assessment = (
            signal_detection_service.analyze(
                signal=signal,
            )
        )

        if assessment is None:
            raise ValueError(
                "Signal analysis failed."
            )

        logger.info(
            "Status=SUCCESS | "
            "Node=SIGNAL_ANALYSIS | "
            "Workflow=%s | "
            "Severity=%s",
            workflow_id,
            assessment.severity.value,
        )

        return {
            "signal_assessment": assessment,
            "current_node": "signal_analysis_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "signal_analysis_node",
                    "message": (
                        f"Signal assessed with "
                        f"severity="
                        f"{assessment.severity.value}"
                    ),
                }
            ],
        }

    except Exception as exc:

        logger.exception(
            "Status=FAILED | "
            "Node=SIGNAL_ANALYSIS | "
            "Workflow=%s | "
            "SignalId=%s | "
            "SignalType=%s | "
            "Error=%s",
            workflow_id,
            signal.signal_id,
            signal.signal_type.value,
            str(exc),
        )

        raise
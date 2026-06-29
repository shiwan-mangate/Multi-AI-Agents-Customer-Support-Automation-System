from datetime import datetime, UTC
from typing import Dict, Any

from layer_2_proactive_agent.database.session import (
    SessionLocal,
)
from layer_2_proactive_agent.repositories.proactive_outreach_repository import (
    ProactiveOutreachRepository,
)
from layer_2_proactive_agent.services.suppression_service import (
    SuppressionService,
)
from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)
from layer_2_proactive_agent.utils.logger import (
    logger,
)

# NOTE: No global variables here!

def suppression_gate_node(
    state: ProactiveState,
) -> Dict[str, Any]:
    """
    Checks whether a customer is currently
    under an active suppression window.
    """

    signal = state["signal"]
    workflow_id = state["workflow_id"]

    logger.info(
        "Status=START | "
        "Node=SUPPRESSION_GATE | "
        "Workflow=%s | Customer=%s",
        workflow_id,
        signal.customer_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    # Open database session inside the function
    db = SessionLocal()

    try:
        # Instantiate repo and service using the session
        repo = ProactiveOutreachRepository(
            session=db
        )

        suppression_service = SuppressionService(
            repo=repo
        )

        suppressed, record_id = (
            suppression_service.should_suppress(
                customer_id=signal.customer_id,
                signal_type=signal.signal_type,
            )
        )

        if suppressed:
            logger.info(
                "Status=SUPPRESSED | "
                "Workflow=%s | "
                "Customer=%s | "
                "Record=%s",
                workflow_id,
                signal.customer_id,
                record_id,
            )

            return {
                "suppressed": True,
                "suppression_reason": (
                    f"Active suppression "
                    f"record={record_id}"
                ),
                "current_node": "suppression_gate_node",
                "workflow_logs": [
                    {
                        "timestamp": timestamp,
                        "node": "suppression_gate_node",
                        "message": (
                            f"Suppressed "
                            f"customer_id={signal.customer_id}"
                        ),
                    }
                ],
            }

        logger.info(
            "Status=NOT_SUPPRESSED | "
            "Workflow=%s | Customer=%s",
            workflow_id,
            signal.customer_id,
        )

        return {
            "suppressed": False,
            "suppression_reason": None,
            "current_node": "suppression_gate_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "suppression_gate_node",
                    "message": (
                        "No active suppression found."
                    ),
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Status=FAILED | "
            "Node=SUPPRESSION_GATE | "
            "Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )
        raise

    finally:
        # Always clean up the database connection
       SessionLocal.remove()
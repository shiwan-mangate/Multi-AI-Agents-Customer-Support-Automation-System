from uuid import uuid4

from layer_2_proactive_agent.schemas.signal import Signal
from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)

from layer_2_proactive_agent.utils.logger import (
    logger,
)


class ProactiveStateFactory:
    """
    Creates initial LangGraph workflow state.
    Every proactive workflow starts here.
    """

    @staticmethod
    def create(
        signal: Signal,
    ) -> ProactiveState:

        workflow_id = f"PRO-{uuid4()}"

        logger.info(
            "Status=STATE_CREATED | "
            "Workflow=%s | "
            "Signal=%s",
            workflow_id,
            signal.signal_id,
        )

        return ProactiveState(
            workflow_id=workflow_id,
            signal_id=signal.signal_id,
            signal=signal,

            customer_profile=None,

            signal_assessment=None,
            risk_assessment=None,
            decision=None,

            outreach_message=None,
            escalation_handoff=None,
            output=None,

            suppressed=False,
            suppression_reason=None,

            current_node="START",

            workflow_logs=[],
            errors=[],
        )
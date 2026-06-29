import os
from datetime import datetime, UTC
from typing import Dict, Any

from langchain_groq import ChatGroq

from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.services.message_generation_service import MessageGenerationService
from layer_2_proactive_agent.services.suppression_service import SuppressionService
from layer_2_proactive_agent.repositories.proactive_outreach_repository import ProactiveOutreachRepository
from layer_2_proactive_agent.database.session import SessionLocal
from layer_2_proactive_agent.utils.logger import logger

# ==========================================
# 🟢 FIX: Initialize the LLM client here 
# ==========================================
_llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=2
)
# Pass the LLM into the service!
message_generation_service = MessageGenerationService(llm=_llm)


def message_generation_node(state: ProactiveState) -> Dict[str, Any]:
    """
    Generates a personalized outreach message using the LLM layer,
    and registers the successful outreach in the suppression database.

    Verified against DB constraints:
    - customer_id -> bigint (int)
    - workflow_id/signal_id -> character varying (str)
    """
    workflow_id = state["workflow_id"]
    customer_profile = state["customer_profile"]
    risk_assessment = state["risk_assessment"]
    signal_assessment = state["signal_assessment"]
    signal = state["signal"]
    decision = state["decision"]

    logger.info(
        "Status=START | Node=MESSAGE_GENERATION | Workflow=%s",
        workflow_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:
        missing_context = []
        if customer_profile is None:
            missing_context.append("customer_profile")
        if risk_assessment is None:
            missing_context.append("risk_assessment")
        if signal_assessment is None:
            missing_context.append("signal_assessment")
        if decision is None:
            missing_context.append("decision")

        if missing_context:
            raise ValueError(
                f"Missing required context for message generation: {', '.join(missing_context)}"
            )

        # 1. Generate the LLM Message
        outreach_message = message_generation_service.generate(
            customer_profile=customer_profile,
            risk_assessment=risk_assessment,
            signal_assessment=signal_assessment,
        )

        # 2. Persist the Outreach to the Registry with safe transaction handling
        with SessionLocal() as db:
            try:
                repo = ProactiveOutreachRepository(session=db)
                suppression_service = SuppressionService(repo=repo)
                
                # Defensive guard to extract action whether it is an Enum object or a raw string
                action_obj = getattr(decision, "action", None)
                action_value = action_obj.value if hasattr(action_obj, "value") else str(action_obj)

                record = suppression_service.create_outreach_record(
                    workflow_id=workflow_id,
                    signal_id=signal.signal_id,
                    customer_id=signal.customer_id,
                    signal_type=signal.signal_type,
                    decision=action_value,
                )
                suppression_service.save_outreach(record)
                db.commit()
            except Exception:
                db.rollback()  # Prevent dirty session states on database failure
                raise

        logger.info(
            "Status=SUCCESS | Node=MESSAGE_GENERATION | Workflow=%s | Subject=%s | GeneratedBy=%s",
            workflow_id,
            outreach_message.subject,
            outreach_message.generated_by,
        )

        return {
            "outreach_message": outreach_message,
            "current_node": "message_generation_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "message_generation_node",
                    "message": (
                        f"Generated outreach message via {outreach_message.generated_by} "
                        f"for channel={outreach_message.channel} and recorded in registry."
                    ),
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Status=FAILED | Node=MESSAGE_GENERATION | Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )
        raise
## layer_1/app/nodes/supervisor_node.py
import logging
from pydantic import ValidationError


from layer_1.app.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from layer_1.app.prompts.retry_prompt import RETRY_PROMPT 
from layer_1.app.utils.parser import load_json
from layer_1.app.models.supervisor_output import SupervisorOutput

logger = logging.getLogger("supervisor_node")

def supervisor_node(unified_ticket: dict, llm, max_retries: int = 2) -> SupervisorOutput:
    """
    Orchestrates Layer 1 with robust error handling and self-healing loops.
    Ensures graceful degradation to human escalation upon multiple AI failures.
    """
    retry_message = ""

    history = unified_ticket.get(
    "conversation_history",
    []
)
    
    logger.warning(
    "HISTORY COUNT = %s",
    len(
        unified_ticket.get(
            "conversation_history",
            []
        )
    )
)
    logger.warning(
    "HISTORY = %s",
    unified_ticket.get(
        "conversation_history",
        []
    )
)
   
    formatted_prompt = SUPERVISOR_PROMPT.format(
        ticket_id=unified_ticket.get("ticket_id"),
        customer_context=unified_ticket.get("customer"),
        normalized_message=unified_ticket.get("message", {}).get("normalized"),
        metadata=unified_ticket.get("metadata"),
        conversation_history=history,
    )

    current_response_text = ""
    
    for attempt in range(max_retries + 1):
        logger.info(f"Ticket {unified_ticket.get('ticket_id')} | Processing Attempt {attempt + 1}")
        
        try:
            prompt_to_send = formatted_prompt if attempt == 0 else retry_message
            raw_response = llm.invoke(prompt_to_send)
            current_response_text = raw_response.content
        except Exception as e:
            logger.error(f"LLM Invocation Failed on attempt {attempt + 1}: {str(e)}")
            current_response_text = "" 

        parsed_data = load_json(current_response_text)
        
        if parsed_data is not None:
            try:
                output = SupervisorOutput(**parsed_data)
                logger.info(f"Route Success: {output.route_to} for ticket {output.ticket_id}")
                return output
            except ValidationError as ve:
                error_context = str(ve)
                logger.warning(f"Schema Validation Failed (Attempt {attempt + 1}): {error_context}")
        else:
            error_context = "JSON Decoding Failed - Check syntax or markdown wrappers."
            logger.warning(f"Parsing Failed (Attempt {attempt + 1})")

        if attempt < max_retries:
            logger.info("Initiating Self-Healing Loop...")
            retry_message = RETRY_PROMPT.format(
                invalid_response=current_response_text or "EMPTY_RESPONSE",
                error_message=error_context,
                schema=SupervisorOutput.model_json_schema() 
            )
        else:
            logger.error(f"Critical Degradation: Escalating ticket {unified_ticket.get('ticket_id')}")
            return SupervisorOutput(
                ticket_id=unified_ticket.get("ticket_id"),
                intent="angry_complex",
                confidence=0,
                sentiment="neutral",
                urgency="high",
                decision_summary="System failure: AI response unrecoverable after multiple retries.",
                route_to="escalation_agent",
                review_required=True,
                clarifying_question=None, 
                entities={},
                supervisor_notes="EMERGENCY ESCALATION: AI_PIPELINE_FAILURE"
            )
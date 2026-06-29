from uuid import uuid4

from layer_2_proactive_agent.schemas.proactive_output import (
    ProactiveOutput,
)
from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
)

from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
    EventMetadata,
    TicketMetadata,
    CustomerMetadata,
    ResolutionMetadata,
    RiskMetadata,
    DecisionMetadata,
    AnalyticsMetadata,
    ConversationMetadata,
)

from layer_2_proactive_agent.utils.logger import (
    logger,
)


class ProactiveAdapter:
    """
    Adapter that translates the internal ProactiveOutput 
    into the canonical CRMResolvedEvent contract.
    """

    def to_crm_event(
        self,
        output: ProactiveOutput,
    ) -> CRMResolvedEvent:
        
        logger.info(
            "Status=START | "
            "Operation=ADAPT_PROACTIVE_OUTPUT | "
            "Workflow=%s",
            output.workflow_id,
        )

        try:

            if output.status == OutreachStatus.SUPPRESSED:
                event_type = "ticket.resolved"
                status = "duplicate_suppressed"
                res_type = "proactive_suppression"
                reason = "Suppressed by cooldown rules."
                resolved_by = "proactive_agent_suppression_engine"

            elif output.status == OutreachStatus.ESCALATION_REQUIRED:
                event_type = "ticket.escalated"
                status = "escalated"
                res_type = "proactive_escalation"
                reason = output.decision.reason if output.decision else "Escalation requested."
                resolved_by = "proactive_agent_router"

            elif output.status == OutreachStatus.OUTREACH_CREATED:
                event_type = "ticket.resolved"
                status = "resolved"
                res_type = "proactive_outreach"
                reason = output.decision.reason if output.decision else "Proactive outreach sent."
                resolved_by = (
                    output.outreach_message.generated_by 
                    if output.outreach_message 
                    else "proactive_agent_llm"
                )

            # FIX 2: Corrected to match the actual Enum value NO_ACTION
            elif output.status == OutreachStatus.NO_ACTION:
                event_type = "ticket.resolved"
                status = "resolved"
                res_type = "proactive_no_action"
                reason = output.decision.reason if output.decision else "Risk below action threshold."
                resolved_by = "proactive_agent_decision_engine"

            else:
                event_type = "ticket.failed"
                status = "failed"
                res_type = "proactive_failure"
                reason = f"Unknown workflow status: {output.status}"
                resolved_by = "system"

            
            event_meta = EventMetadata(
                event_id=str(uuid4()),
                event_type=event_type,
                source_agent=output.agent_id,
            )

            ticket_meta = TicketMetadata(
                ticket_id=(
                    output.escalation_handoff.ticket_id 
                    if output.escalation_handoff 
                    else f"TKT-{output.workflow_id}"
                ),
                workflow_id=output.workflow_id,
                channel=(
                    output.outreach_message.channel 
                    if output.outreach_message 
                    else "system"
                ),
            )

       
            customer_meta = CustomerMetadata(
                customer_id=output.customer_id,
            )

            resolution_meta = ResolutionMetadata(
                status=status,
                resolution_type=res_type,
                resolution_message=reason,
                resolved_by=resolved_by,
            )

            risk_meta = RiskMetadata(
                escalated=(status == "escalated"),
                human_review_required=(
                    output.decision.review_required if output.decision else False
                ),
                risk_level=(
                    output.risk_assessment.risk_level.value 
                    if output.risk_assessment 
                    else "low"
                ),
            )

            decision_meta = DecisionMetadata(
                decision_code=output.decision.action.value if output.decision else None,
                decision_reason=reason,
                review_required=output.decision.review_required if output.decision else False,
            )

      
            intent_val = "angry_complex"

            analytics_meta = AnalyticsMetadata(
                intent=intent_val,
                issue_tags=[intent_val, res_type],
                priority=(
                    output.risk_assessment.risk_level.value 
                    if output.risk_assessment 
                    else None
                ),
            )

            conversation_meta = None
            if output.outreach_message:
                conversation_meta = ConversationMetadata(
                    messages=[
                        {
                            "role": "assistant",
                            "subject": output.outreach_message.subject,
                            "content": output.outreach_message.body,
                        }
                    ],
                    agents_involved=[output.agent_id],
                    original_message=output.outreach_message.body,
                    translated_message=output.outreach_message.body,
                )

            
            crm_event = CRMResolvedEvent(
                event=event_meta,
                ticket=ticket_meta,
                customer=customer_meta,
                resolution=resolution_meta,
                risk=risk_meta,
                decision=decision_meta,
                analytics=analytics_meta,
                conversation=conversation_meta,
            )

            logger.info(
                "Status=SUCCESS | "
                "Operation=ADAPT_PROACTIVE_OUTPUT | "
                "Workflow=%s | "
                "EventType=%s",
                output.workflow_id,
                event_type,
            )

            return crm_event
            
        except Exception as exc:
            
            logger.exception(
                "Status=FAILED | "
                "Operation=ADAPT_PROACTIVE_OUTPUT | "
                "Workflow=%s | Error=%s",
                output.workflow_id,
                str(exc),
            )
            
            raise
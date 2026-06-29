import uuid
import logging
from fastapi import BackgroundTasks, HTTPException, status
from api.schemas.ticket_requests import ContinueConversationRequest
from api.schemas.ticket_responses import ContinueConversationResponse
from platform_orchestration.dependency_container import DependencyContainer
from platform_orchestration.inbound_ticket_pipeline import InboundTicketPipeline
from api.schemas.ticket_requests import InboundTicketRequest
from api.schemas.ticket_responses import TicketAcceptedResponse, TicketStatusResponse, TicketStatus
from api.schemas.ticket_messages_responses import (
    TicketMessagesResponse
)
from api.schemas.ticket_responses import (
    TicketTraceResponse,
    TraceStepResponse
)
from api.schemas.ticket_conversation_responses import (
    TicketMessagesResponse,
    MessageItem
)
logger = logging.getLogger("api_ticket_service")

class TicketService:
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.pipeline = InboundTicketPipeline(container)
    
    def _run_pipeline_in_background(self, payload: dict, request_id: str):
        """Silently executes the AI pipeline. Catches and logs all failures."""
        ticket_id = payload.get("ticket_id", "UNKNOWN")
        logger.info(f"[{request_id}]  Background Task Started for Ticket: {ticket_id}")

        try:
            self.pipeline.process(payload)
            logger.info(f"[{request_id}]  Background Task Completed for Ticket: {ticket_id}")
        except Exception as e:
            logger.error(f"[{request_id}]  Background Pipeline Failed for {ticket_id}: {e}", exc_info=True)

            
    def submit_ticket_async(
        self, 
        request: InboundTicketRequest, 
        background_tasks: BackgroundTasks, 
        request_id: str
    ) -> TicketAcceptedResponse:
        """
        Ingests the ticket, enforces the Golden Thread ID, and queues the background job.
        """
        ticket_id = f"TKT-{uuid.uuid4().hex[:12].upper()}"
        payload = request.model_dump()
        payload["ticket_id"] = ticket_id
        background_tasks.add_task(self._run_pipeline_in_background, payload, request_id)
        return TicketAcceptedResponse(
            status=TicketStatus.PROCESSING,
            detail="Ticket accepted and routed to the autonomous AI platform.",
            ticket_id=ticket_id
        )
    
    def get_ticket_status(self, ticket_id: str, request_id: str) -> TicketStatusResponse:
        """
        Determines the exact state of the ticket by checking active workflows and historical transcripts.
        """
        logger.info(f"[{request_id}] Fetching exact status for ticket: {ticket_id}")

        try:
            workflow = self.container.workflow_repository.get(ticket_id)
            if workflow:
                return TicketStatusResponse(
                    ticket_id=ticket_id,
                    status=TicketStatus.PAUSED,
                    agent_type=workflow.agent_type,
                    workflow_status=workflow.status
                )
            
            transcript = self.container.crm_transcript_repository.get_by_ticket_id(ticket_id)
            if transcript:
                return TicketStatusResponse(
                    ticket_id=ticket_id,
                    status=TicketStatus.COMPLETED,
                    agent_type=getattr(transcript, "source_agent", "unknown"),
                   workflow_status=getattr(transcript, "status", "resolved")
                )
            
            return TicketStatusResponse(
                ticket_id=ticket_id,
                status=TicketStatus.PROCESSING,
                agent_type=None,
                workflow_status=None
            )
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch ticket status: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database Lookup Failed,While Fetching Ticket Status"
            )
        

    def continue_conversation(self,ticket_id: str,request: ContinueConversationRequest,background_tasks: BackgroundTasks,request_id: str) -> ContinueConversationResponse:
        """
        Continue an existing customer conversation using the
        original CRM transcript and customer profile.
        """

        logger.info(
            f"[{request_id}] Continuing conversation for Ticket {ticket_id}"
        )

        try:

            transcript = (
                self.container.crm_transcript_repository
                .get_by_ticket_id(ticket_id)
            )

            if not transcript:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket {ticket_id} not found."
                )


            profile = (
                self.container.crm_customer_profile_repository
                .get_profile(transcript.customer_id)
            )

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer profile not found for ticket {ticket_id}."
                )


            payload = {
                "ticket_id": ticket_id,
                "customer_id": transcript.customer_id,

                "name": getattr(
                    profile,
                    "customer_name",
                    profile.customer_email
                ),

                "channel": transcript.channel,
                "message": request.message,

                # Future-ready
                "conversation_history": getattr(
                    transcript,
                    "messages",
                    []
                )
            }
            background_tasks.add_task(
                self._run_pipeline_in_background,
                payload,
                request_id
            )

            logger.info(
                f"[{request_id}] Continuation queued for Ticket {ticket_id}"
            )
            return ContinueConversationResponse(
                ticket_id=ticket_id,
                status="queued",
                detail="Conversation continuation accepted and queued."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"[{request_id}] Failed continuing conversation "
                f"for {ticket_id}: {e}",
                exc_info=True
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to continue conversation."
            )
        
    def get_ticket_messages(self,ticket_id: str,request_id: str) -> TicketMessagesResponse:

        logger.info(
            f"[{request_id}] Fetching conversation for {ticket_id}"
        )

        transcript = (
            self.container.crm_transcript_repository
            .get_by_ticket_id(ticket_id)
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found."
            )

        messages = [
            MessageItem(
                role=msg.get("role", "unknown"),
                content=msg.get("content", "")
            )
            for msg in (transcript.messages or [])
        ]

        return TicketMessagesResponse(
            ticket_id=ticket_id,
            total_messages=len(messages),
            messages=messages
        )
    def get_ticket_trace(self,ticket_id: str,request_id: str) -> TicketTraceResponse:

        logger.info(
            f"[{request_id}] Fetching trace for ticket {ticket_id}"
        )

        traces = (
            self.container.workflow_trace_repository
            .get_ticket_trace(ticket_id)
        )

        if not traces:
            raise HTTPException(
                status_code=404,
                detail=f"No trace found for ticket {ticket_id}"
            )

        steps = [
            TraceStepResponse(
                stage=t.stage,
                status=t.status,
                details=t.details,
                created_at=t.created_at
            )
            for t in traces
        ]

        return TicketTraceResponse(
            ticket_id=ticket_id,
            total_steps=len(steps),
            steps=steps
        )
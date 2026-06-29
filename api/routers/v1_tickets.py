from functools import lru_cache
from fastapi import APIRouter, Depends, BackgroundTasks, status, Path

from api.dependencies import get_container, get_request_id
from api.schemas.ticket_requests import InboundTicketRequest
from api.schemas.ticket_responses import TicketAcceptedResponse, TicketStatusResponse
from api.services.ticket_service import TicketService
from api.schemas.ticket_requests import ContinueConversationRequest
from api.schemas.ticket_responses import ContinueConversationResponse
from api.schemas.ticket_conversation_responses import (
    TicketMessagesResponse
)
from api.schemas.ticket_responses import (
    TicketTraceResponse
)

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])

@lru_cache()
def get_ticket_service() -> TicketService:
    """
    Caches the TicketService singleton.
    Calls the cached get_container() directly to avoid re-instantiating 
    the InboundTicketPipeline on every HTTP request.
    """
    return TicketService(get_container())

@router.post(
    "/",
    name="submit_ticket",
    response_model=TicketAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a new support ticket",
    description="Queues a ticket for asynchronous processing through the AI orchestration layers."
)
def submit_ticket(
    request: InboundTicketRequest,
    background_tasks: BackgroundTasks,
    service: TicketService = Depends(get_ticket_service),
    request_id: str = Depends(get_request_id)
):
    return service.submit_ticket_async(request, background_tasks, request_id)

@router.get(
    "/{ticket_id}",
    name="get_ticket_status",
    response_model=TicketStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ticket status",
    description="Returns the exact processing state of a ticket workflow, checking active queues and CRM transcripts."
)
def get_ticket_status(
    ticket_id: str = Path(
        ..., 
        description="Platform ticket identifier", 
        examples=["TKT-F24A3F545D36"]
    ),
    service: TicketService = Depends(get_ticket_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_ticket_status(ticket_id, request_id)

@router.post(
    "/{ticket_id}/continue",
    name="continue_conversation",
    response_model=ContinueConversationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Continue Existing Conversation",
    description="Adds a new customer message to an existing ticket and re-runs the AI orchestration workflow."
)
def continue_conversation(
    request: ContinueConversationRequest,
    background_tasks: BackgroundTasks,
    ticket_id: str = Path(
        ...,
        description="Existing ticket identifier",
        examples=["TKT-F24A3F545D36"]
    ),
    service: TicketService = Depends(get_ticket_service),
    request_id: str = Depends(get_request_id)
):
    return service.continue_conversation(
        ticket_id=ticket_id,
        request=request,
        background_tasks=background_tasks,
        request_id=request_id
    )

@router.get(
    "/{ticket_id}/messages",
    response_model=TicketMessagesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ticket Conversation"
)
def get_ticket_messages(
    ticket_id: str,
    service: TicketService = Depends(get_ticket_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_ticket_messages(
        ticket_id=ticket_id,
        request_id=request_id
    )

@router.get(
    "/{ticket_id}/trace",
    response_model=TicketTraceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get workflow trace"
)
def get_ticket_trace(
    ticket_id: str,
    service: TicketService = Depends(
        get_ticket_service
    ),
    request_id: str = Depends(
        get_request_id
    )
):
    return service.get_ticket_trace(
        ticket_id,
        request_id
    )
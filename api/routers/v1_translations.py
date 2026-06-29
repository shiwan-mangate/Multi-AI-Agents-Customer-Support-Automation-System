from functools import lru_cache
from fastapi import APIRouter, Depends, status, Path, Query

from api.dependencies import get_container, get_request_id
from api.schemas.translation_requests import LiveTranslationRequest
from api.schemas.translation_responses import (
    CustomerTranslationHistoryResponse,
    TranslationRecordItem,
    LiveTranslationResponse,
    OperationsDashboardResponse
)
from api.services.translation_service import TranslationApiService

router = APIRouter(prefix="/api/v1/translations", tags=["Translations (Layer 3)"])

@lru_cache()
def get_translation_service() -> TranslationApiService:
    return TranslationApiService(get_container())

# FIXED: Cleaned up URL from /dashboard/operations to /analytics
@router.get(
    "/analytics",
    name="get_translation_analytics",
    response_model=OperationsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Translation Analytics Dashboard",
    description="Returns Layer 3 system health, success/failure rates, and active language distribution."
)
def get_translation_analytics(
    limit: int = Query(100, ge=1, le=1000, description="Max failure records to return"),
    service: TranslationApiService = Depends(get_translation_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_operations_dashboard(limit=limit, request_id=request_id)

@router.get(
    "/tickets/{ticket_id}",
    name="get_ticket_translation",
    response_model=TranslationRecordItem,
    status_code=status.HTTP_200_OK,
    summary="Ticket Translation Audit Log",
    description="Retrieves the exact bidirectional translation record for a specific ticket."
)
def get_ticket_translation(
    ticket_id: str = Path(..., description="The Ticket ID to lookup"),
    service: TranslationApiService = Depends(get_translation_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_ticket_translation(ticket_id, request_id)

# FIXED: Added safe pagination limits to the customer history endpoint
@router.get(
    "/customers/{customer_id}",
    name="get_customer_translation_history",
    response_model=CustomerTranslationHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Customer Translation History",
    description="Retrieves the chronological list of all translations generated for a specific customer."
)
def get_customer_history(
    customer_id: int = Path(..., ge=1, description="The Customer ID to lookup"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of history records to retrieve"),
    service: TranslationApiService = Depends(get_translation_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_customer_history(customer_id=customer_id, limit=limit, request_id=request_id)

@router.post(
    "/{ticket_id}/translate",
    name="execute_live_translation",
    response_model=LiveTranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Live Outbound Translation",
    description="Takes English text from a human manager, applies Tone Rules, translates it, and updates the ticket's outbound audit log."
)
def live_translate(
    request: LiveTranslationRequest,
    ticket_id: str = Path(..., description="The Ticket ID to attach this translation to"),
    service: TranslationApiService = Depends(get_translation_service),
    request_id: str = Depends(get_request_id)
):
    return service.live_translate(ticket_id, request, request_id)
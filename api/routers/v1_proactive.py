from functools import lru_cache
from fastapi import APIRouter, Depends, status, Path, BackgroundTasks
from fastapi.params import Query

from api.dependencies import get_container, get_request_id
from api.schemas.proactive_responses import (
    ProactiveHistoryResponse,
    ActiveSuppressionsResponse,
    ActiveSignalsResponse,
    RunScanResponse,
    RecentEventsResponse
)
from api.services.proactive_service import ProactiveService

router = APIRouter(prefix="/api/v1/proactive", tags=["Proactive Outreach"])

@lru_cache()
def get_proactive_service() -> ProactiveService:
    return ProactiveService(get_container())

@router.post(
    "/run-scan",
    name="trigger_proactive_scan",
    response_model=RunScanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Proactive Scanner",
    description="Manually triggers the CRM signal detection and dispatches non-suppressed signals to the proactive LangGraph workflow asynchronously."
)
def run_scan(
    background_tasks: BackgroundTasks,
    service: ProactiveService = Depends(get_proactive_service),
    request_id: str = Depends(get_request_id)
):
    return service.run_scan_async(background_tasks, request_id)

@router.get(
    "/signals",
    name="preview_active_signals",
    response_model=ActiveSignalsResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview Active Signals",
    description="Runs the CRM signal detection logic without triggering any workflows. Excellent for debugging and UI radar dashboards."
)
def preview_active_signals(
    service: ProactiveService = Depends(get_proactive_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_active_signals(request_id)

@router.get(
    "/history/{customer_id}",
    name="get_proactive_history",
    response_model=ProactiveHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Customer Outreach History",
    description="Retrieves a complete log of all proactive events, including success, failure, and escalation states."
)
def get_customer_proactive_history(
    customer_id: int = Path(..., ge=1),
    service: ProactiveService = Depends(get_proactive_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_customer_history(customer_id, request_id)

@router.get(
    "/suppressions/{customer_id}",
    name="get_customer_suppressions",
    response_model=ActiveSuppressionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Active Customer Suppressions",
    description="Retrieves all active cooldowns and their reasons, explaining why a customer is not being messaged."
)
def get_customer_suppressions(
    customer_id: int = Path(..., ge=1),
    service: ProactiveService = Depends(get_proactive_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_active_suppressions(customer_id, request_id)

@router.get(
    "/events",
    name="get_recent_events",
    response_model=RecentEventsResponse,
    status_code=status.HTTP_200_OK,
    summary="Recent Proactive Events",
    description="Retrieves a global chronological log of all recent proactive workflows across all customers. Perfect for admin activity streams."
)
def get_recent_events(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of recent events to retrieve"),
    service: ProactiveService = Depends(get_proactive_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_recent_events(limit=limit, request_id=request_id)
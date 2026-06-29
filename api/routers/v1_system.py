from functools import lru_cache
from fastapi import APIRouter, Depends, status, Path, Query

from api.dependencies import get_container, get_request_id
from api.schemas.system_responses import (
    SystemStatusResponse,
    ActiveWorkflowsResponse,
    WorkflowDetailResponse
)
from api.services.system_service import SystemService

router = APIRouter(prefix="/api/v1/system", tags=["System & Operations"])

@lru_cache()
def get_system_service() -> SystemService:
    """Singleton caching for the System Operations Service."""
    return SystemService(get_container())

@router.get(
    "/status",
    name="get_system_status",
    response_model=SystemStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get System Status",
    description="Returns the health and connectivity pulse of core database and platform components."
)
def get_system_status(
    service: SystemService = Depends(get_system_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_system_status(request_id=request_id)

@router.get(
    "/workflows",
    name="get_active_workflows",
    response_model=ActiveWorkflowsResponse,
    status_code=status.HTTP_200_OK,
    summary="List Active Workflows",
    description="Returns a list of all currently running or paused LangGraph orchestrator workflows."
)
def get_active_workflows(
    limit: int = Query(100, ge=1, le=1000, description="Max number of workflows to retrieve"),
    service: SystemService = Depends(get_system_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_active_workflows(limit=limit, request_id=request_id)

@router.get(
    "/workflows/{ticket_id}",
    name="get_workflow_details",
    response_model=WorkflowDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Workflow Details",
    description="Returns the execution details and LangGraph thread_id for a specific ticket's workflow."
)
def get_workflow_details(
    ticket_id: str = Path(..., description="The unique Platform Ticket ID"),
    service: SystemService = Depends(get_system_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_workflow_details(ticket_id=ticket_id, request_id=request_id)
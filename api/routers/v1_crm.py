from functools import lru_cache
from typing import List
from fastapi import APIRouter, Depends, status, Path


from api.dependencies import get_container, get_request_id
from api.schemas.crm_responses import (
    CustomerProfileResponse, 
    CustomerTimelineResponse,
    ChurnAlertResponse
)
from api.services.crm_service import CRMService

router = APIRouter(prefix="/api/v1/crm", tags=["CRM & Customer Data"])

@lru_cache()
def get_crm_service() -> CRMService:
    """Singleton caching for the CRM Service."""
    return CRMService(get_container())

@router.get(
    "/customers/{customer_id}",
    name="get_customer_profile",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Customer Profile",
    description="Returns the aggregated CRM memory, LTV, and current churn risk for a specific customer."
)
def get_customer_profile(
    customer_id: int = Path(
        ..., 
        ge=1,
        description="Unique database ID of the customer", 
        examples=[1]
    ),
    service: CRMService = Depends(get_crm_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_customer_profile(customer_id, request_id)

@router.get(
    "/customers/{customer_id}/timeline",
    name="get_customer_timeline",
    response_model=CustomerTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Customer Timeline",
    description="Returns a chronologically sorted history of all agent interactions and AI actions for a customer."
)
def get_customer_timeline(
    customer_id: int = Path(
        ..., 
        ge=1, 
        description="Unique database ID of the customer", 
        examples=[1]
    ),
    service: CRMService = Depends(get_crm_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_customer_timeline(customer_id, request_id)

@router.get(
    "/churn-alerts",
    name="get_churn_alerts",
    response_model=List[ChurnAlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve Active Churn Alerts",
    description="Fetches a list of all active/pending churn alerts requiring human or automated intervention."
)
def get_churn_alerts(
    service: CRMService = Depends(get_crm_service),
    request_id: str = Depends(get_request_id)
):
    """Provides a global view of accounts at risk of churning."""
    return service.get_active_churn_alerts(request_id)
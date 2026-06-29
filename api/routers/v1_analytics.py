from functools import lru_cache
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from layer_4_analytics.schemas.roi_metrics import ROIMetrics
from api.dependencies import get_container, get_request_id
from api.schemas.analytics_responses import MasterDashboardResponse
from api.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["Layer 4 Analytics"])

@lru_cache()
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(get_container())

@router.get(
    "/dashboard",
    name="get_master_dashboard",
    response_model=MasterDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Master Analytics Dashboard"
)
def get_master_dashboard(
    days: int = Query(30, ge=1, le=365),
    service: AnalyticsService = Depends(get_analytics_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_master_dashboard(
        days=days,
        request_id=request_id
    )

@router.get(
    "/customers/{customer_id}/roi",
    response_model=ROIMetrics,
    summary="Customer ROI Report",
)
def get_customer_roi(
    customer_id: int,
    days: int = Query(30, ge=1, le=365),
    service: AnalyticsService = Depends(get_analytics_service),
    request_id: str = Depends(get_request_id),
):
    return service.get_customer_roi(
        customer_id=customer_id,
        days=days,
        request_id=request_id,
    )
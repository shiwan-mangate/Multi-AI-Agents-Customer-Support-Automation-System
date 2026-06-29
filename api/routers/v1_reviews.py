from functools import lru_cache
from fastapi import APIRouter, Depends, status, Path

from api.dependencies import get_container, get_request_id
from api.schemas.review_requests import ReviewActionRequest
from api.schemas.review_responses import PendingReviewsResponse, PendingReviewItem, ReviewOutcomeResponse
from api.services.review_service import ReviewService

router = APIRouter(prefix="/api/v1/reviews", tags=["Human Review (HITL)"])

@lru_cache()
def get_review_service() -> ReviewService:
    return ReviewService(get_container())

@router.get(
    "/pending",
    name="get_pending_reviews",
    response_model=PendingReviewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Pending Reviews",
    description="Returns a list of all paused workflows waiting for a manager's decision."
)
def get_pending_reviews(
    service: ReviewService = Depends(get_review_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_pending_reviews(limit=50, request_id=request_id)

@router.get(
    "/{ticket_id}",
    name="get_review_by_ticket",
    response_model=PendingReviewItem,
    status_code=status.HTTP_200_OK,
    summary="Get Specific Review",
    description="Fetches the exact state of a single paused workflow for detailed UI rendering."
)
def get_review(
    ticket_id: str = Path(..., description="The Ticket ID to lookup"),
    service: ReviewService = Depends(get_review_service),
    request_id: str = Depends(get_request_id)
):
    return service.get_review(ticket_id, request_id)

@router.post(
    "/{ticket_id}/decision",
    name="submit_review_decision",
    response_model=ReviewOutcomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Human Decision",
    description="Submits a manager's decision (APPROVE, REJECT, or REQUEST_CLARIFICATION) to resume a paused workflow."
)
def submit_review_decision(
    request: ReviewActionRequest,
    ticket_id: str = Path(..., description="The Ticket ID to review"),
    service: ReviewService = Depends(get_review_service),
    request_id: str = Depends(get_request_id)
):
    return service.process_decision(ticket_id, request, request_id)
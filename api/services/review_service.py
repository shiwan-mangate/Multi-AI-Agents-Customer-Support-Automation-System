import logging
from fastapi import HTTPException, status
from platform_orchestration.dependency_container import DependencyContainer
from platform_orchestration.inbound_ticket_pipeline import InboundTicketPipeline

from api.schemas.review_requests import ReviewActionRequest
from api.schemas.review_responses import PendingReviewsResponse, PendingReviewItem, ReviewOutcomeResponse

logger = logging.getLogger("api_review_service")


class ReviewService:
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.pipeline = InboundTicketPipeline(self.container)

    def get_pending_reviews(self, limit: int = 50, request_id: str = "unknown") -> PendingReviewsResponse:
        """
        Fetches the queue of paused tickets for the Manager Dashboard.
        """
        logger.info(f"[{request_id}] Fetching HITL queue (limit: {limit})")
        try:
            records = self.container.workflow_repository.get_all_pending(limit=limit)
            
            items = [
                PendingReviewItem(
                    workflow_id=r.workflow_id,
                    ticket_id=r.ticket_id,
                    agent_type=r.agent_type,
                    status=r.status
                ) for r in records
            ]
            
            return PendingReviewsResponse(
                total_pending=len(items), 
                reviews=items
            )
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch review queue: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Database error retrieving pending reviews."
            )
        
    def get_review(self, ticket_id: str, request_id: str = "unknown") -> PendingReviewItem:
            """Fetches a specific paused workflow for the Manager detailed view."""
            logger.info(f"[{request_id}] Fetching specific review for Ticket {ticket_id}")
            
            try:
                record = self.container.workflow_repository.get(ticket_id)
                
                if not record:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Pending review for ticket {ticket_id} not found or already processed."
                    )
                    
                return PendingReviewItem(
                    workflow_id=record.workflow_id,
                    ticket_id=record.ticket_id,
                    agent_type=record.agent_type,
                    status=record.status
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"[{request_id}] Failed to fetch review {ticket_id}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail="Database error retrieving the pending review."
                )
    def process_decision(
        self, 
        ticket_id: str, 
        request: ReviewActionRequest, 
        request_id: str = "unknown"
    ) -> ReviewOutcomeResponse:
        """
        Resumes the LangGraph workflow based on the manager's payload.
        """
        logger.info(f"[{request_id}] Applying {request.decision} to Ticket {ticket_id} by {request.reviewer_id}")
        
        try:
        
            result = self.pipeline.resume_specialist_workflow(
                ticket_id=ticket_id, 
                human_decision=request.decision, 
                reviewer_id=request.reviewer_id,
                notes=request.notes
            )

            logger.warning(
            "RESUME RESULT = %s",
            result
        )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Cannot resume. No active/paused workflow found for ticket {ticket_id}."
                )

            
            customer_facing_response = None

            # 1. Preferred path -> translated response
            customer_res = result.get("customer_response")

            if customer_res:
                customer_facing_response = (
                    customer_res.get("customer_response")
                    if isinstance(customer_res, dict)
                    else customer_res
                )

            # 2. Fallback -> specialist output response
            if not customer_facing_response:

                specialist_result = result.get(
                    "specialist_result"
                )

                if specialist_result:

                    customer_facing_response = getattr(
                        specialist_result,
                        "customer_response",
                        None
                    )
            return ReviewOutcomeResponse(
            ticket_id=ticket_id,
            status="COMPLETED",
            decision_applied=request.decision,
            customer_facing_response=customer_facing_response
        )
        
        except HTTPException:
            raise  
        except Exception as e:
            logger.error(f"[{request_id}] Failed to process HITL review for {ticket_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error resuming specialist workflow."
            )
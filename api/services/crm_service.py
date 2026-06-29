import logging
from fastapi import HTTPException, status
from platform_orchestration.dependency_container import DependencyContainer
from typing import List
from api.schemas.crm_responses import (
    CustomerProfileResponse, 
    CustomerTimelineResponse, 
    TimelineEvent,
    ChurnAlertResponse
)

logger = logging.getLogger("api_crm_service")

class CRMService:
    def __init__(self, container: DependencyContainer):
        self.container = container

    def get_customer_profile(self, customer_id: int, request_id: str) -> CustomerProfileResponse:
        logger.info(f"[{request_id}] Fetching profile for Customer {customer_id}")
        try:
            profile = self.container.crm_customer_profile_repository.get_profile(customer_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer {customer_id} not found in the CRM."
                )
            return CustomerProfileResponse(
                customer_id=profile.customer_id,
                customer_email=profile.customer_email,
                tier=getattr(profile, "tier", "standard"),
                ltv=float(getattr(profile, "ltv", 0.0)),
                total_tickets=getattr(profile, "total_tickets", 0),
                churn_score=(
                    float(profile.churn_score) 
                    if getattr(profile, "churn_score", None) is not None 
                    else None
                ),
                churn_level=getattr(profile, "churn_level", None),
                last_sentiment=getattr(profile, "last_sentiment", "neutral"),
                negative_ticket_count=getattr(profile, "negative_ticket_count", 0)
            )
        except HTTPException:
            raise  
        except Exception as e:
            logger.error(f"[{request_id}] DB error fetching profile {customer_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve CRM profile data."
            )
    
    def get_customer_timeline(self, customer_id: int, request_id: str) -> CustomerTimelineResponse:
        logger.info(f"[{request_id}] Generating chronological timeline for Customer {customer_id}")
        try:
            profile = self.container.crm_customer_profile_repository.get_profile(customer_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Cannot fetch timeline. Customer {customer_id} not found."
                )
            
            transcripts = self.container.crm_transcript_repository.get_customer_history(customer_id, limit=50)
            timeline_events = []
            for t in transcripts:
                timeline_events.append(
                    TimelineEvent(
                        event_id=f"transcript-{t.ticket_id}",
                        event_type="transcript",
                        timestamp=t.created_at,
                        title=f"Ticket {t.status.capitalize()} by {t.source_agent}",
                        description=f"Intent: {t.intent} | Resolution: {t.resolution_type}",
                        metadata={
                            "ticket_id": t.ticket_id,
                            "channel": t.channel,
                            "sentiment": t.sentiment_end,
                            "time_to_resolve_ms": t.time_to_resolution_ms
                        }
                    )
                )

            timeline_events.sort(key=lambda x: x.timestamp, reverse=True)
            return CustomerTimelineResponse(
                customer_id=customer_id,
                total_events=len(timeline_events), 
                events=timeline_events
            )
        except HTTPException:
            raise  
        except Exception as e:
            logger.error(f"[{request_id}] DB error fetching timeline {customer_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve customer timeline data."
            )

    def get_active_churn_alerts(self, request_id: str, limit: int = 50) -> List[ChurnAlertResponse]:
        """Fetches all open/pending risk alerts for the dashboard."""
        logger.info(f"[{request_id}] Fetching active churn alerts")
        try:
            # We utilize the existing pending delivery method to grab active alerts
            alerts = self.container.churn_alert_repository.get_pending_delivery_alerts(batch_size=limit)
            
            return [
                ChurnAlertResponse(
                    alert_id=a.alert_id,
                    customer_id=a.customer_id,
                    alert_type=a.alert_type,
                    severity=a.severity,
                    reason=a.reason,
                    status=a.alert_status,
                    created_at=a.created_at
                ) for a in alerts
            ]
        except Exception as e:
            logger.error(f"[{request_id}] DB error fetching churn alerts: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve active churn alerts."
            ) 
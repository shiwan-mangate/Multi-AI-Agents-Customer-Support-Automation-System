from datetime import datetime, UTC, timedelta
from typing import List, Dict, Any

from sqlalchemy import select, func, desc, case, Integer
from sqlalchemy.orm import Session

from crm_agent.db.models.customer_profile_model import CustomerProfile
from crm_agent.db.models.transcript_model import TranscriptRecord
from crm_agent.db.models.feedback_model import FeedbackSignal


class AnalyticsRepository:
    """
    Read-Only Data Access Layer for Business Intelligence.
    Powers the Metabase/Grafana dashboards and the AnalyticsService.
    Strictly aggregates data; NEVER writes or updates records.
    """
    
    def __init__(self, session: Session):
        self.session = session


    def get_agent_performance_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Calculates volume, speed, and escalation rates per agent.
        Maps directly to AgentPerformanceMetrics schema.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = (
            select(
                TranscriptRecord.resolved_by.label("agent_name"),
                func.count(TranscriptRecord.ticket_id).label("tickets_handled"),
                # Casted to Integer to align perfectly with schema data representations
                func.coalesce(
                    func.cast(func.avg(TranscriptRecord.time_to_resolution_ms), Integer), 
                    0
                ).label("avg_resolution_time_ms"),
                
                func.count(case((TranscriptRecord.status == 'escalated', 1))).label("escalations"),
                func.count(case((TranscriptRecord.status == 'failed', 1))).label("failures")
            )
            .where(TranscriptRecord.created_at >= cutoff)
            .group_by(TranscriptRecord.resolved_by)
        )
        
        results = self.session.execute(stmt).mappings().all()
        return [dict(row) for row in results]

    def get_agent_csat_scores(self, days: int = 30) -> List[Dict[str, Any]]:
        """Calculates the average customer rating per agent."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = (
            select(
                FeedbackSignal.source_agent.label("agent_name"),
                func.avg(FeedbackSignal.rating).label("average_rating"),
                func.count(FeedbackSignal.feedback_id).label("feedback_count")
            )
            .where(FeedbackSignal.created_at >= cutoff)
            .group_by(FeedbackSignal.source_agent)
        )
        
        results = self.session.execute(stmt).mappings().all()
        return [dict(row) for row in results]


    def get_intent_volume_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Identifies what issues are spiking right now.
        Maps to IntentMetrics schema.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = (
            select(
                TranscriptRecord.intent,
                func.count(TranscriptRecord.ticket_id).label("ticket_count")
            )
            .where(TranscriptRecord.created_at >= cutoff)
            .where(TranscriptRecord.intent.is_not(None))
            .group_by(TranscriptRecord.intent)
            .order_by(desc("ticket_count"))
            .limit(20)
        )
        
        results = self.session.execute(stmt).mappings().all()
        return [dict(row) for row in results]


    def get_churn_segmentation(self) -> Dict[str, int]:
        """
        Calculates the current global health of the customer base.
        Maps to ChurnDistributionMetrics schema.
        """
        stmt = (
            select(
                CustomerProfile.churn_level,
                func.count(CustomerProfile.customer_id).label("customer_count")
            )
            .group_by(CustomerProfile.churn_level)
        )
        
        results = self.session.execute(stmt).all()
        

        distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "URGENT": 0}
        for level, count in results:
            if level in distribution:
                distribution[level] = count
                
        return distribution

    def get_refund_financials(self, days: int = 30) -> Dict[str, Any]:
        """
        Aggregates specific business metrics for the Refund workflow.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = (
            select(
                func.count(TranscriptRecord.ticket_id).label("total_refunds_processed"),
                func.count(case((TranscriptRecord.status == 'denied', 1))).label("refund_rejections"),
            )
            .where(TranscriptRecord.created_at >= cutoff)
            .where(TranscriptRecord.source_agent == 'refund_agent')
        )
        
        result = self.session.execute(stmt).mappings().first()
        return dict(result) if result else {}
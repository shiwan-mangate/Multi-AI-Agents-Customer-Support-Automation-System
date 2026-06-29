# layer_4_analytics/repositories/analytics_repository.py

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case

# Centralized imports across the layers
from crm_agent.db.models.transcript_model import TranscriptRecord
from layer_3.database.models.translation_record_model import TranslationRecordModel
from layer_2_triage.database.model.customer_model import Customer
from crm_agent.db.models.customer_profile_model import CustomerProfile

class AnalyticsRepository:
    """
    The exclusive Data Access Object (DAO) for Layer 4.
    Strictly read-only. Extracts raw transactional logs from PostgreSQL.
    SQL is perfectly mapped to the actual database schema via SQLAlchemy ORM.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_platform_summary(self, period_start: datetime, period_end: datetime) -> Dict[str, int]:
        """
        Extracts top-level volumetric hero metrics for the DashboardSnapshot.
        Source: ticket_transcripts
        """
        result = self.db.query(
            func.count(TranscriptRecord.id).label('total_tickets'),
            func.count(func.distinct(TranscriptRecord.customer_id)).label('total_customers')
        ).filter(
            TranscriptRecord.created_at >= period_start,
            TranscriptRecord.created_at < period_end
        ).first()

        return {
            "total_tickets": result.total_tickets if result and result.total_tickets else 0,
            "total_customers": result.total_customers if result and result.total_customers else 0
        }

    def get_agent_data(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """
        Extracts raw execution logs for specialist agents.
        Source: ticket_transcripts
        """
        results = self.db.query(
            TranscriptRecord.resolved_by.label('agent_name'),
            TranscriptRecord.status,
            TranscriptRecord.time_to_resolution_ms
        ).filter(
            TranscriptRecord.created_at >= period_start,
            TranscriptRecord.created_at < period_end,
            TranscriptRecord.resolved_by.isnot(None)
        ).all()

        return [row._asdict() for row in results]

    def get_intent_data(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """
        Extracts raw Layer 1 routing classifications.
        Source: ticket_transcripts
        """
        results = self.db.query(
            TranscriptRecord.intent
        ).filter(
            TranscriptRecord.created_at >= period_start,
            TranscriptRecord.created_at < period_end,
            TranscriptRecord.intent.isnot(None)
        ).all()

        return [row._asdict() for row in results]

    def get_feedback_data(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """
        Extracts raw customer satisfaction signals and text context directly from transcripts.
        Source: ticket_transcripts
        """
        results = self.db.query(
            TranscriptRecord.feedback.label("feedback_type"),
            TranscriptRecord.intent.label('topic'),
            TranscriptRecord.original_message.label('question')
        ).filter(
            TranscriptRecord.created_at >= period_start,
            TranscriptRecord.created_at < period_end,
            TranscriptRecord.feedback.isnot(None)
        ).all()

        return [row._asdict() for row in results]

    def get_language_data(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """
        Extracts translation engine health and volume markers.
        Source: translation_records
        """
        results = (
    self.db.query(
        TranslationRecordModel.ticket_id,
        TranslationRecordModel.original_language.label("language_code"),
        TranslationRecordModel.translation_success.label("translation_success"),
    )
    .filter(
        TranslationRecordModel.created_at >= period_start,
        TranslationRecordModel.created_at < period_end,
    )
    .distinct(
        TranslationRecordModel.ticket_id,
        TranslationRecordModel.original_language,
    )
    .all()
)

        rows = [row._asdict() for row in results]
        
        # 🟢 TEMPORARY DEBUG DUMP
        print("\n" + "="*50)
        print("🚨 ANALYTICS REPOSITORY DEBUG 🚨")
        print("get_language_data rows[:5]:")
        for i, row in enumerate(rows[:5]):
            print(f"Row {i}: {row}")
        print("="*50 + "\n")

        return rows

    def get_all_customer_churn_data(self) -> List[Dict[str, Any]]:
        """
        Reads the churn metrics already computed by the CRM engine.
        No business logic is performed here.
        """
        results = (
            self.db.query(
                CustomerProfile.customer_id,
                Customer.name.label("customer_name"),
                CustomerProfile.churn_score.label("churn_risk_score"),
                CustomerProfile.last_sentiment.label("last_sentiment_score"),
                CustomerProfile.repeat_negative_count.label("unresolved_ticket_count"),
                CustomerProfile.last_ticket_at,
            )
            .outerjoin(
                Customer,
                Customer.customer_id == CustomerProfile.customer_id,
            )
            .all()
        )
        rows = []
        now = datetime.utcnow()
        for row in results:
            last_activity = row.last_ticket_at
            if last_activity:
                delta = now - last_activity.replace(tzinfo=None)
                days_since_last_activity = max(delta.days, 0)
            else:
                days_since_last_activity = 999
            rows.append(
                {
                    "customer_id": row.customer_id,
                    "customer_name": row.customer_name,
                    "churn_risk_score": row.churn_risk_score,
                    "last_sentiment_score": row.last_sentiment_score,
                    "unresolved_ticket_count": row.unresolved_ticket_count,
                    "days_since_last_activity": days_since_last_activity,
                }
            )
        return rows

    def get_customer_churn_data(self, risk_threshold: int) -> List[Dict[str, Any]]:
        """
        Returns customers whose churn score exceeds the specified threshold.
        Reads directly from the CRM customer profile table.
        """

        results = (
            self.db.query(
                CustomerProfile.customer_id,
                Customer.name.label("customer_name"),
                CustomerProfile.churn_score.label("churn_risk_score"),
                CustomerProfile.last_sentiment.label("last_sentiment_score"),
                CustomerProfile.negative_ticket_count.label("unresolved_ticket_count"),
                CustomerProfile.last_ticket_at,
            )
            .outerjoin(
                Customer,
                Customer.customer_id == CustomerProfile.customer_id,
            )
            .filter(
                CustomerProfile.churn_score >= risk_threshold
            )
            .all()
        )

        rows = []

        now = datetime.utcnow()

        for row in results:
            last_activity = row.last_ticket_at
            if last_activity:
                delta = now - last_activity.replace(tzinfo=None)
                days_since_last_activity = max(delta.days, 0)
            else:
                days_since_last_activity = 999

            rows.append(
                {
                    "customer_id": row.customer_id,
                    "customer_name": row.customer_name,
                    "churn_risk_score": (
                        float(row.churn_risk_score)
                        if row.churn_risk_score is not None
                        else 0.0
                    ),
                    "last_sentiment_score": row.last_sentiment_score,
                    "unresolved_ticket_count": row.unresolved_ticket_count,
                    "days_since_last_activity": days_since_last_activity,
                }
            )

        return rows

    def get_roi_data(self, period_start: datetime, period_end: datetime, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extracts raw volume matrices for financial conversions, joining to retrieve client names.
        Source: ticket_transcripts JOIN customers
        """
        query = self.db.query(
            TranscriptRecord.customer_id,
            Customer.name.label('customer_name'),
            TranscriptRecord.resolution_type,
            TranscriptRecord.status
        ).outerjoin(
            Customer, TranscriptRecord.customer_id == Customer.customer_id
        ).filter(
            TranscriptRecord.created_at >= period_start,
            TranscriptRecord.created_at < period_end
        )

        if customer_id is not None:
            query = query.filter(TranscriptRecord.customer_id == customer_id)

        results = query.all()
        return [row._asdict() for row in results]
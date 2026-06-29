# platform_orchestration/builders/build_crm.py

# ==========================================
# REPOSITORIES
# ==========================================
from crm_agent.repositories.analytics_repository import AnalyticsRepository
from crm_agent.repositories.churn_alert_repository import ChurnAlertRepository
from crm_agent.repositories.customer_event_repository import CRMEventRepository
from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository
from crm_agent.repositories.feedback_repository import FeedbackRepository
from crm_agent.repositories.processed_event_repository import ProcessedEventRepository
from crm_agent.repositories.transcript_repository import TranscriptRepository

# ==========================================
# ADAPTERS
# ==========================================
from crm_agent.adapters.account_adapter import AccountAdapter
from crm_agent.adapters.escalation_adapter import EscalationAdapter
from crm_agent.adapters.faq_adapter import FAQAdapter
from crm_agent.adapters.refund_adapter import RefundAdapter

# ==========================================
# SERVICES (Mapped exactly to your directory)
# ==========================================
from crm_agent.services.alerts.alert_service import AlertService
from crm_agent.services.alerts.slack_notifier import SlackNotifier

from crm_agent.services.analytics.analytics_service import AnalyticsService
from crm_agent.services.analytics.metrics_aggregator import MetricsAggregator

from crm_agent.services.churn.churn_engine import ChurnEngine
from crm_agent.services.churn.churn_service import ChurnService

from crm_agent.services.customer.profile_service import ProfileService

from crm_agent.services.ingestion.event_claim_service import EventClaimService
from crm_agent.services.ingestion.idempotency_service import IdempotencyService

from crm_agent.services.processing.event_router import EventRouter
from crm_agent.services.processing.pipeline_executor import PipelineExecutor

from crm_agent.services.transcript.transcript_service import TranscriptService


def build_crm(container):
    # 1. Repositories (Data Access Layer)
    container.crm_analytics_repository = AnalyticsRepository(container.db)
    container.churn_alert_repository = ChurnAlertRepository(container.db)
    container.crm_event_repository = CRMEventRepository(container.db)
    container.crm_customer_profile_repository = CustomerProfileRepository(container.db)
    container.feedback_repository = FeedbackRepository(container.db)
    container.processed_event_repository = ProcessedEventRepository(container.db)
    container.crm_transcript_repository = TranscriptRepository(container.db)
    
    # 2. Adapters (Orchestrator to CRM Data Mappers)
    container.crm_adapters = {
        "account_agent": AccountAdapter(),
        "escalation_agent": EscalationAdapter(),
        "faq_agent": FAQAdapter(),
        "refund_agent": RefundAdapter(),
    }

    # 3. Core/Stateless Utilities
    container.event_router = EventRouter()
    container.churn_engine = ChurnEngine()
    container.idempotency_service = IdempotencyService(container.processed_event_repository)
    
    # 4. Domain Services
    container.transcript_service = TranscriptService(container.crm_transcript_repository)
    container.profile_service = ProfileService(container.crm_customer_profile_repository)
    
    container.churn_service = ChurnService(
        churn_engine=container.churn_engine, 
        profile_repo=container.crm_customer_profile_repository
    )
    
    container.alert_service = AlertService(container.churn_alert_repository)
    container.slack_notifier = SlackNotifier(container.churn_alert_repository)

    container.analytics_service = AnalyticsService(container.crm_analytics_repository)
    container.metrics_aggregator = MetricsAggregator(container.analytics_service)
    
    # 5. Queue & Pipeline Orchestration Services
    container.event_claim_service = EventClaimService(container.crm_event_repository)
    
    container.pipeline_executor = PipelineExecutor(
        transcript_service=container.transcript_service,
        profile_service=container.profile_service,
        churn_service=container.churn_service,
        alert_service=container.alert_service
    )
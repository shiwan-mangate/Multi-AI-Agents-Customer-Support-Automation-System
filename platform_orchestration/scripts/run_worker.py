# platform_orchestration/scripts/run_worker.py

import sys
import os
# Force Python to look two folders up (at your root directory) to fix module import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging
from crm_agent.db.connection import SessionLocal
from platform_orchestration.dependency_container import DependencyContainer

# Repositories
from crm_agent.repositories.customer_event_repository import CRMEventRepository
from crm_agent.repositories.transcript_repository import TranscriptRepository
from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository
from crm_agent.repositories.churn_alert_repository import ChurnAlertRepository
from crm_agent.repositories.processed_event_repository import ProcessedEventRepository

# Services
from crm_agent.services.ingestion.event_consumer import CRMEventConsumer
from crm_agent.services.ingestion.event_claim_service import EventClaimService
from crm_agent.services.processing.event_processor import EventProcessor
from crm_agent.services.ingestion.idempotency_service import IdempotencyService

# Set up basic logging so we can watch the daemon work
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("worker_main")

def main():
    logger.info("Initializing Dependency Container (Stateless Assets Only)...")
    container = DependencyContainer()

    def processor_factory(session):
        # 🟢 FIX: Create brand new repositories bound strictly to THIS transaction's session.
        # This prevents the worker from accidentally using the orchestrator's global DB lock.
        fresh_event_repo = CRMEventRepository(session)
        fresh_transcript_repo = TranscriptRepository(session)
        fresh_profile_repo = CustomerProfileRepository(session)
        fresh_alert_repo = ChurnAlertRepository(session)
        fresh_processed_repo = ProcessedEventRepository(session)

        # The IdempotencyService needs the fresh processed repo to function correctly
        fresh_idempotency_service = IdempotencyService(fresh_processed_repo)

        return EventProcessor(
            session=session,
            router=container.event_router,       # Safe to reuse (stateless logic)
            churn_engine=container.churn_engine, # Safe to reuse (stateless math)
            idempotency_service=fresh_idempotency_service,
            event_repo=fresh_event_repo,
            transcript_repo=fresh_transcript_repo,
            profile_repo=fresh_profile_repo,
            alert_repo=fresh_alert_repo,
        )

    def claim_service_factory(session):
        # 🟢 FIX: The Claim Service also needs a fresh repository to lock rows safely!
        fresh_event_repo = CRMEventRepository(session)
        return EventClaimService(fresh_event_repo)

    logger.info("Booting up CRM Event Consumer...")
    consumer = CRMEventConsumer(
        session_factory=SessionLocal,
        processor_factory=processor_factory,
        claim_service_factory=claim_service_factory,
        batch_size=5,
        idle_sleep_seconds=2.0
    )

    # Start the infinite polling loop
    consumer.start()

if __name__ == "__main__":
    main()
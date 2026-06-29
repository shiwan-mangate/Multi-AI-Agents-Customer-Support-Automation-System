# crm_agent/run_worker.py

import logging
import os
import signal
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


from crm_agent.repositories.customer_event_repository import (
    CRMEventRepository,
)

from crm_agent.repositories.transcript_repository import (
    TranscriptRepository,
)

from crm_agent.repositories.customer_profile_repository import (
    CustomerProfileRepository,
)

from crm_agent.repositories.churn_alert_repository import (
    ChurnAlertRepository,
)

from crm_agent.repositories.processed_event_repository import (
    ProcessedEventRepository,
)


from crm_agent.services.transcript.transcript_service import (
    TranscriptService,
)

from crm_agent.services.customer.profile_service import (
    ProfileService,
)

from crm_agent.services.churn.churn_engine import (
    ChurnEngine,
)

from crm_agent.services.churn.churn_service import (
    ChurnService,
)

from crm_agent.services.alerts.alert_service import (
    AlertService,
)

from crm_agent.services.ingestion.idempotency_service import (
    IdempotencyService,
)

from crm_agent.services.ingestion.event_claim_service import (
    EventClaimService,
)


from crm_agent.services.processing.event_router import (
    EventRouter,
)

from crm_agent.services.processing.pipeline_executor import (
    PipelineExecutor,
)

from crm_agent.services.processing.event_processor import (
    EventProcessor,
)

from crm_agent.services.ingestion.event_consumer import (
    CRMEventConsumer,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)



def build_claim_service(
    session: Session,
) -> EventClaimService:
    """
    Factory used by the consumer when claiming
    events from the distributed queue.
    """

    event_repo = CRMEventRepository(session)

    return EventClaimService(
        event_repo=event_repo,
    )



def build_processor(
    session: Session,
) -> EventProcessor:
    """
    Creates a fully wired EventProcessor
    for a single transaction scope.
    """

    # -----------------------------------------------------
    # Repositories
    # -----------------------------------------------------
    event_repo = CRMEventRepository(session)

    transcript_repo = TranscriptRepository(
        session
    )

    profile_repo = CustomerProfileRepository(
        session
    )

    alert_repo = ChurnAlertRepository(
        session
    )

    processed_repo = ProcessedEventRepository(
        session
    )

    # -----------------------------------------------------
    # Core Engines
    # -----------------------------------------------------
    churn_engine = ChurnEngine()

    # -----------------------------------------------------
    # Services
    # -----------------------------------------------------
    transcript_service = TranscriptService(
        transcript_repo=transcript_repo,
    )

    profile_service = ProfileService(
        profile_repo=profile_repo,
    )

    churn_service = ChurnService(
        churn_engine=churn_engine,
        profile_repo=profile_repo,
    )

    alert_service = AlertService(
        alert_repo=alert_repo,
    )

    idempotency_service = IdempotencyService(
        processed_repo=processed_repo,
    )

    # -----------------------------------------------------
    # Orchestration Layer
    # -----------------------------------------------------
    router = EventRouter()

    executor = PipelineExecutor(
        transcript_service=transcript_service,
        profile_service=profile_service,
        churn_service=churn_service,
        alert_service=alert_service,
    )

    # -----------------------------------------------------
    # Event Processor
    # -----------------------------------------------------
    processor = EventProcessor(
        session=session,
        router=router,
        pipeline_executor=executor,
        idempotency_service=idempotency_service,
        event_repo=event_repo,
    )

    return processor


# =========================================================
# Application Entry Point
# =========================================================
def main() -> None:

    logger.info(
        "Initializing CRM Background Worker..."
    )

    # -----------------------------------------------------
    # Database
    # -----------------------------------------------------
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/crm_db",
    )

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    # -----------------------------------------------------
    # Consumer
    # -----------------------------------------------------
    consumer = CRMEventConsumer(
        session_factory=session_factory,
        processor_factory=build_processor,
        claim_service_factory=build_claim_service,
        batch_size=10,
        idle_sleep_seconds=2.0,
    )

    # -----------------------------------------------------
    # Graceful Shutdown
    # -----------------------------------------------------
    def shutdown_handler(
        signum,
        frame,
    ):
        logger.warning(
            "Shutdown signal received. "
            "Stopping worker gracefully..."
        )

        consumer.stop()

        sys.exit(0)

    signal.signal(
        signal.SIGINT,
        shutdown_handler,
    )

    signal.signal(
        signal.SIGTERM,
        shutdown_handler,
    )

    # -----------------------------------------------------
    # Start Worker
    # -----------------------------------------------------
    try:

        logger.info(
            "CRM Worker started."
        )

        consumer.start()

    except Exception as e:

        logger.critical(
            "Fatal worker failure | error=%s",
            str(e),
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
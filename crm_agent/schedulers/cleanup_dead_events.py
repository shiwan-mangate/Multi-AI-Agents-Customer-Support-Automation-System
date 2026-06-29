import argparse
import logging
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crm_agent.repositories.customer_event_repository import (
    CRMEventRepository,
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

logger = logging.getLogger(
    "cleanup_cron"
)


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Prune expired DEAD events."
        )
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Retention period in days.",
    )

    args = parser.parse_args()

    logger.info(
        "Initializing Queue Cleanup Job..."
    )

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/crm_db",
    )

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=2,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    with SessionLocal() as session:

        repo = CRMEventRepository(
            session
        )

        logger.info(
            "Scanning for DEAD events older than %d days...",
            args.days,
        )

        try:

            deleted_count = (
                repo.cleanup_dead_events(
                    retention_days=args.days
                )
            )

            session.commit()

            if deleted_count > 0:

                logger.info(
                    "Garbage Collection Complete | purged=%d",
                    deleted_count,
                )

            else:

                logger.info(
                    "Garbage Collection Complete | nothing to purge"
                )

        except Exception as e:

            session.rollback()

            logger.exception(
                "Cleanup job failed | error=%s",
                str(e),
            )

            sys.exit(1)


if __name__ == "__main__":
    main()
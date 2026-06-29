# crm_agent/scripts/replay_failed_events.py

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

logger = logging.getLogger("replay_tool")


def main() -> None:
    """
    Requeue FAILED CRM events.

    Example:

    python replay_failed_events.py --limit 500
    """

    parser = argparse.ArgumentParser(
        description="Replay FAILED CRM events."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum events to replay.",
    )

    args = parser.parse_args()

    logger.info(
        "Initializing Replay Tool..."
    )

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/crm_db",
    )

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
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
            "Scanning for up to %d FAILED events...",
            args.limit,
        )

        try:

            requeued_count = (
                repo.replay_failed_events(
                    limit=args.limit
                )
            )

            session.commit()

            if requeued_count > 0:

                logger.info(
                    "Successfully requeued %d FAILED events.",
                    requeued_count,
                )

            else:

                logger.info(
                    "No FAILED events found. Queue is healthy."
                )

        except Exception as e:

            session.rollback()

            logger.exception(
                "Replay failed | error=%s",
                str(e),
            )

            sys.exit(1)


if __name__ == "__main__":
    main()
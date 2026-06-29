from functools import lru_cache
from typing import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from platform_orchestration.dependency_container import DependencyContainer
from crm_agent.db.connection import SessionLocal

import logging

logger = logging.getLogger("api_dependencies")


@lru_cache()
def get_container() -> DependencyContainer:
    """
    Global singleton dependency container.
    """
    logger.info("Initializing Dependency Container...")
    return DependencyContainer()


def get_db_session() -> Generator[Session, None, None]:
    """
    Per-request database session.
    """
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def get_request_id(request: Request) -> str:
    """
    Extract request ID from middleware.
    """
    return getattr(request.state, "request_id", "unknown")
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=1800,
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
except Exception as e:
    logger.exception(f"Failed to initialize standalone Escalation DB engine: {e}")
    raise


def get_db():
    """Contextual generator for standalone operations fallback."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
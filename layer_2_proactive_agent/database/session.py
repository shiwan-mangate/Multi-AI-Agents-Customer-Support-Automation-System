from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from layer_2_proactive_agent.config.settings import settings
from dotenv import load_dotenv
load_dotenv()
import os

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
)


SessionLocal = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
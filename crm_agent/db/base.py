from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Master blueprint registry for all PostgreSQL tables in the CRM.
    All ORM models must inherit from this class so Alembic can track their metadata.
    """
    pass
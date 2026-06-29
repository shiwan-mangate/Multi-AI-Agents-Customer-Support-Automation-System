from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from crm_agent.db.base import Base


from crm_agent.db.models.crm_event_model import CRMEvent
from crm_agent.db.models.processed_event_model import ProcessedEvent
from crm_agent.db.models.transcript_model import TranscriptRecord
from crm_agent.db.models.customer_profile_model import CustomerProfile
from crm_agent.db.models.churn_alert_model import ChurnAlert
from crm_agent.db.models.feedback_model import FeedbackSignal
from layer_3.database.models.translation_record_model import TranslationRecordModel


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Restrict Alembic to CRM tables only.
    Prevent touching existing operational platform tables.
    """
    managed_tables  = {
        "crm_events",
        "processed_events",
        "ticket_transcripts",
        "customer_support_profiles",
        "churn_alerts",
        "feedback_signals",
        "translation_records"
    }

    if type_ == "table":
        return name in managed_tables 

    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
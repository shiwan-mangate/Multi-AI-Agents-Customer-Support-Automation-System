# Codebase Inventory and Documentation Report

This document serves as an onboarding inventory for engineers exploring the codebase. It details the folder structure, all discovered files, and provides a structured file-by-file analysis of classes, methods, schemas, enums, functions, and constants.

---

## Section 1: Folder Structure

```text
demorepo/
│
├── adapters/
│   ├── __init__.py
│   ├── account_adapter.py
│   ├── base_adapter.py
│   ├── escalation_adapter.py
│   ├── faq_adapter.py
│   └── refund_adapter.py
│
├── dashboards/
│   └── metabase_setup.md
│
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── connection.py
│   ├── migrations/
│   │   ├── README
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 5bfb7b38709d_create_crm_tables.py
│   │       ├── a8c3f1b2d9e7_create_proactive_tables.py
│   │       └── b1b3ec865383_create_translation_records_table.py
│   └── models/
│       ├── __init__.py
│       ├── churn_alert_model.py
│       ├── crm_event_model.py
│       ├── customer_profile_model.py
│       ├── feedback_model.py
│       ├── processed_event_model.py
│       └── transcript_model.py
│
├── docs/
│   ├── architecture.md
│   ├── churn_formula.md
│   ├── dashboard_metrics.md
│   └── event_contract.md
│
├── repositories/
│   ├── __init__.py
│   ├── analytics_repository.py
│   ├── churn_alert_repository.py
│   ├── customer_event_repository.py
│   ├── customer_profile_repository.py
│   ├── feedback_repository.py
│   ├── processed_event_repository.py
│   └── transcript_repository.py
│
├── schedulers/
│   ├── cleanup_dead_events.py
│   └── refresh_views.py
│
├── schemas/
│   ├── __init__.py
│   ├── alert.py
│   ├── analytics.py
│   ├── churn.py
│   ├── crm_event.py
│   ├── customer_profile.py
│   └── transcript.py
│
├── scripts/
│   ├── replay_failed_events.py
│   ├── run_refresh_scheduler.py
│   └── run_worker.py
│
├── services/
│   ├── __init__.py
│   ├── alerts/
│   │   ├── alert_service.py
│   │   └── slack_notifier.py
│   ├── analytics/
│   │   ├── analytics_service.py
│   │   └── metrics_aggregator.py
│   ├── churn/
│   │   ├── churn_engine.py
│   │   └── churn_service.py
│   ├── customer/
│   │   ├── issue_tag_service.py
│   │   ├── language_service.py
│   │   ├── profile_service.py
│   │   └── sentiment_service.py
│   ├── ingestion/
│   │   ├── event_claim_service.py
│   │   ├── event_consumer.py
│   │   └── idempotency_service.py
│   ├── processing/
│   │   ├── event_processor.py
│   │   ├── event_router.py
│   │   └── pipeline_executor.py
│   └── transcript/
│       └── transcript_service.py
│
├── tests/
│   ├── fixtures/
│   │   ├── account_payloads.py
│   │   ├── common.py
│   │   ├── escalation_payloads.py
│   │   ├── faq_payloads.py
│   │   └── refund_payloads.py
│   ├── integration/
│   │   ├── test_alert_flow.py
│   │   ├── test_customer_updates.py
│   │   ├── test_end_to_end_crm_flow.py
│   │   ├── test_event_pipeline.py
│   │   └── test_transcript_persistence.py
│   └── unit/
│       ├── test_adapters.py
│       ├── test_churn_engine.py
│       ├── test_event_claiming.py
│       ├── test_idempotency.py
│       └── test_profile_updates.py
│
├── .gitignore
├── README.md
├── alembic.ini
├── config.py
├── constants.py
├── main.py
└── requirements.txt
```

---

## Section 2: File Analysis

### File: `config.py`
* **Purpose**: Configuration setup declaring standard setting values for database authentication.
* **Classes**:
  * **Class**: `Settings`
    * **Type**: Other (Configuration Class)
    * **Methods**: None
    * **Purpose**: Holds default configuration variables for database connections.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `db_user`
  * `db_pass`
  * `db_host`
  * `db_port`
  * `db_name`
  * `settings`
* **Relationships**:
  * Consumed by: `db/connection.py`

---

### File: `constants.py`
* **Purpose**: Placeholder file for system-wide constants.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `main.py`
* **Purpose**: Placeholder file for primary execution setup.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `alembic.ini`
* **Purpose**: Configuration file for Alembic database migration environment.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `script_location`
  * `prepend_sys_path`
  * `sqlalchemy.url`
* **Relationships**:
  * Consumed by: Alembic CLI tools and `db/migrations/env.py`

---

### File: `adapters/base_adapter.py`
* **Purpose**: Base abstract adapter defining metadata-builder utilities for specialists.
* **Classes**:
  * **Class**: `BaseAdapter`
    * **Type**: Utility
    * **Methods**:
      * `to_crm_event()`
      * `_build_event_metadata()`
      * `_build_ticket_metadata()`
      * `_build_customer_metadata()`
      * `_build_analytics_metadata()`
      * `_build_conversation_metadata()`
    * **Purpose**: Shared parsing logic mapped to build CRM canonical schemas.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `SCHEMA_VERSION`
* **Relationships**:
  * Used By: `adapters/account_adapter.py`, `adapters/escalation_adapter.py`, `adapters/faq_adapter.py`, `adapters/refund_adapter.py`

---

### File: `adapters/account_adapter.py`
* **Purpose**: Adapts specialist Account Agent outcomes into canonical CRMResolvedEvents.
* **Classes**:
  * **Class**: `AccountAdapter`
    * **Type**: Utility
    * **Methods**:
      * `to_crm_event()`
    * **Purpose**: Specialized parsing to map Account Agent dictionary payloads to Pydantic models.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumes: `adapters/base_adapter.py`
  * Produces: `schemas/crm_event.py` (CRMResolvedEvent)

---

### File: `adapters/escalation_adapter.py`
* **Purpose**: Adapts specialist Escalation Agent outcomes into canonical CRMResolvedEvents.
* **Classes**:
  * **Class**: `EscalationAdapter`
    * **Type**: Utility
    * **Methods**:
      * `to_crm_event()`
    * **Purpose**: Specialized parsing to map Escalation Agent dictionary payloads to Pydantic models.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumes: `adapters/base_adapter.py`
  * Produces: `schemas/crm_event.py` (CRMResolvedEvent)

---

### File: `adapters/faq_adapter.py`
* **Purpose**: Adapts specialist FAQ Agent outcomes into canonical CRMResolvedEvents.
* **Classes**:
  * **Class**: `FAQAdapter`
    * **Type**: Utility
    * **Methods**:
      * `to_crm_event()`
    * **Purpose**: Specialized parsing to map FAQ Agent dictionary payloads to Pydantic models.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumes: `adapters/base_adapter.py`
  * Produces: `schemas/crm_event.py` (CRMResolvedEvent)

---

### File: `adapters/refund_adapter.py`
* **Purpose**: Adapts specialist Refund Agent outcomes into canonical CRMResolvedEvents.
* **Classes**:
  * **Class**: `RefundAdapter`
    * **Type**: Utility
    * **Methods**:
      * `to_crm_event()`
    * **Purpose**: Specialized parsing to map Refund Agent dictionary payloads to Pydantic models.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumes: `adapters/base_adapter.py`
  * Produces: `schemas/crm_event.py` (CRMResolvedEvent)

---

### File: `dashboards/metabase_setup.md`
* **Purpose**: Empty placeholder documentation for dashboards setup.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `db/base.py`
* **Purpose**: Master blueprint DeclarativeBase registry for ORM models.
* **Classes**:
  * **Class**: `Base`
    * **Type**: Other (SQLAlchemy DeclarativeBase)
    * **Methods**: None
    * **Purpose**: Shared metadata repository for tracking migrations.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Inherited by: All SQL models inside `db/models/` and referenced in Alembic `db/migrations/env.py`

---

### File: `db/connection.py`
* **Purpose**: Standard database session construction and transactional scoping generator.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `get_db()`
    * **Parameters**: None
    * **Returns**: `Generator[Session, None, None]`
    * **Purpose**: Yields scoped SQLAlchemy database sessions.
* **Constants**:
  * `DATABASE_URL`
  * `engine`
  * `SessionLocal`
* **Relationships**:
  * Consumed by: worker runtime entry scripts and testing modules.

---

### File: `db/models/churn_alert_model.py`
* **Purpose**: Operational risk alert ledger database schema table definition.
* **Classes**:
  * **Class**: `ChurnAlert`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Defines attributes mapping operational alert records into PostgreSQL table structure.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"churn_alerts"`
  * `__table_args__` = `(Index("idx_alert_suppression", "customer_id", "alert_status", "created_at"), Index("idx_alert_delivery", "delivery_status", "created_at"), Index("idx_alert_ops_dashboard", "alert_status", "severity"))`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `churn_alerts`
  * **Attributes**:
    * `alert_id : String(64) [Primary Key]`
    * `customer_id : BIGINT`
    * `ticket_id : String(64) [Nullable]`
    * `customer_email : String(255) [Nullable]`
    * `tier : String(50)`
    * `ltv : Numeric`
    * `source_agent : String(50) [Nullable]`
    * `alert_type : String(50)`
    * `severity : String(20)`
    * `score : Numeric`
    * `reason : Text`
    * `risk_reasons : ARRAY(String(255))`
    * `alert_status : String(20)`
    * `delivery_status : String(20)`
    * `acknowledged : Boolean`
    * `acknowledged_by : String(100) [Nullable]`
    * `acknowledged_at : DateTime(timezone=True) [Nullable]`
    * `created_at : DateTime(timezone=True)`
    * `updated_at : DateTime(timezone=True)`
* **Relationships**:
  * Managed by: `repositories/churn_alert_repository.py`

---

### File: `db/models/crm_event_model.py`
* **Purpose**: PostgreSQL-backed distributed CRM queue database schema table definition.
* **Classes**:
  * **Class**: `CRMEvent`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Defines columns mapping event ingestion queue status states into database storage.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"crm_events"`
  * `__table_args__` = `(Index("idx_crm_queue_polling", "status", "created_at"),)`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `crm_events`
  * **Attributes**:
    * `event_id : String(64) [Primary Key]`
    * `event_type : String(50)`
    * `source_agent : String(50)`
    * `schema_version : String(20)`
    * `payload : JSONB`
    * `status : String(20)`
    * `retry_count : Integer`
    * `claimed_by : String(100) [Nullable]`
    * `claimed_at : DateTime(timezone=True) [Nullable]`
    * `created_at : DateTime(timezone=True)`
    * `processed_at : DateTime(timezone=True) [Nullable]`
    * `updated_at : DateTime(timezone=True)`
    * `last_error : Text [Nullable]`
* **Relationships**:
  * Managed by: `repositories/customer_event_repository.py`

---

### File: `db/models/customer_profile_model.py`
* **Purpose**: CRM customer profile database schema table definition.
* **Classes**:
  * **Class**: `CustomerProfile`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Defines parameters tracking compiled operational values per customer ID.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"customer_support_profiles"`
  * `__table_args__` = `(Index("idx_customer_churn", "churn_level"), Index("idx_customer_last_ticket", "last_ticket_at"))`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `customer_support_profiles`
  * **Attributes**:
    * `customer_id : BIGINT [Primary Key]`
    * `customer_email : String(255) [Nullable]`
    * `tier : String(50)`
    * `ltv : Numeric`
    * `total_tickets : BIGINT`
    * `total_faq_tickets : BIGINT`
    * `total_refund_tickets : BIGINT`
    * `total_account_tickets : BIGINT`
    * `total_escalations : BIGINT`
    * `total_denials : BIGINT`
    * `total_failures : BIGINT`
    * `total_clarifications : BIGINT`
    * `total_duplicate_suppressions : BIGINT`
    * `repeat_negative_count : BIGINT`
    * `repeat_escalation_count : BIGINT`
    * `duplicate_request_count : BIGINT`
    * `negative_ticket_count : BIGINT`
    * `last_sentiment : String(50) [Nullable]`
    * `sentiment_history : ARRAY(String(50))`
    * `churn_score : Numeric`
    * `churn_level : String(50)`
    * `churn_last_updated : DateTime(timezone=True) [Nullable]`
    * `issue_frequency : JSONB`
    * `agent_interaction_frequency : JSONB`
    * `languages_used : ARRAY(String(10))`
    * `preferred_language : String(10)`
    * `first_seen_at : DateTime(timezone=True)`
    * `last_ticket_at : DateTime(timezone=True) [Nullable]`
    * `updated_at : DateTime(timezone=True)`
    * `created_at : DateTime(timezone=True)`
* **Relationships**:
  * Managed by: `repositories/customer_profile_repository.py`

---

### File: `db/models/feedback_model.py`
* **Purpose**: Customer feedback intelligence database schema table definition.
* **Classes**:
  * **Class**: `FeedbackSignal`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Maps satisfaction responses, ratings, and comments to database structure.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"feedback_signals"`
  * `__table_args__` = `(Index("idx_feedback_customer", "customer_id", "created_at"), Index("idx_feedback_agent", "source_agent", "rating", "created_at"), Index("idx_feedback_ticket", "ticket_id", unique=True))`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `feedback_signals`
  * **Attributes**:
    * `feedback_id : String(64) [Primary Key]`
    * `ticket_id : String(64)`
    * `customer_id : BIGINT`
    * `source_agent : String(50)`
    * `feedback_type : String(50)`
    * `rating : Integer`
    * `comment : Text [Nullable]`
    * `feedback_channel : String(50) [Nullable]`
    * `resolution_type : String(100) [Nullable]`
    * `status : String(50) [Nullable]`
    * `processed_for_churn : Boolean`
    * `created_at : DateTime(timezone=True)`
* **Relationships**:
  * Managed by: `repositories/feedback_repository.py`

---

### File: `db/models/processed_event_model.py`
* **Purpose**: Idempotency tracker schema mapping to prevent double processing.
* **Classes**:
  * **Class**: `ProcessedEvent`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Mapped record schema marking event outcomes in the relational store.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"processed_events"`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `processed_events`
  * **Attributes**:
    * `event_id : String(64) [Primary Key]`
    * `processed_at : DateTime(timezone=True)`
    * `result_status : String(20)`
* **Relationships**:
  * Managed by: `repositories/processed_event_repository.py`

---

### File: `db/models/transcript_model.py`
* **Purpose**: Immutable append-only audit transcript ledger table mapping.
* **Classes**:
  * **Class**: `TranscriptRecord`
    * **Type**: Other (SQLAlchemy ORM Model)
    * **Methods**: None
    * **Purpose**: Maps the full conversation text and analytical traits to relational storage.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `__tablename__` = `"ticket_transcripts"`
  * `__table_args__` = `(Index("idx_transcript_customer", "customer_id", "created_at"), Index("idx_transcript_analytics", "intent", "created_at"), Index("idx_transcript_agent_perf", "resolved_by", "created_at"))`
* **Database Spec**:
  * **Database**: PostgreSQL
  * **Tables Referenced**: `ticket_transcripts`
  * **Attributes**:
    * `id : BigInteger [Primary Key, Autoincrement]`
    * `ticket_id : String(64)`
    * `schema_version : String(20)`
    * `customer_id : BigInteger`
    * `source_agent : String(50)`
    * `workflow_id : String(100) [Nullable]`
    * `trace_id : String(100) [Nullable]`
    * `channel : String(20) [Nullable]`
    * `messages : JSONB`
    * `agents_involved : JSONB`
    * `original_message : Text [Nullable]`
    * `translated_message : Text [Nullable]`
    * `intent : String(100) [Nullable]`
    * `priority : String(20) [Nullable]`
    * `sentiment_start : String(20) [Nullable]`
    * `sentiment_end : String(20) [Nullable]`
    * `issue_tags : ARRAY(String(100))`
    * `status : String(50)`
    * `resolution_type : String(100)`
    * `resolution_message : Text [Nullable]`
    * `resolved_by : String(50)`
    * `time_to_resolution_ms : Integer [Nullable]`
    * `feedback : String(20) [Nullable]`
    * `created_at : DateTime(timezone=True)`
* **Relationships**:
  * Managed by: `repositories/transcript_repository.py`

---

### File: `db/migrations/env.py`
* **Purpose**: Core migration execution script setting target metadata and table authorization bounds.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `include_object()`
    * **Parameters**: `object`, `name`, `type_`, `reflected`, `compare_to`
    * **Returns**: `bool`
    * **Purpose**: Restricts Alembic operations to CRM-specific database tables.
  * **Function**: `run_migrations_offline()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Configures migration script engine execution in offline execution scripts.
  * **Function**: `run_migrations_online()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Binds Alembic context variables to the relational connection session for real-time migrations.
* **Constants**:
  * `config`
  * `target_metadata`
* **Relationships**:
  * Consumes: `db/base.py` (Base)

---

### File: `db/migrations/versions/5bfb7b38709d_create_crm_tables.py`
* **Purpose**: Alembic revision script creating primary CRM operational tables and indexes.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `upgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Executes creation statements for tables: `churn_alerts`, `crm_events`, `customer_support_profiles`, `feedback_signals`, `processed_events`, `ticket_transcripts`.
  * **Function**: `downgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Executes drop statements to roll back table layouts.
* **Constants**:
  * `revision`
  * `down_revision`
  * `branch_labels`
  * `depends_on`
* **Relationships**: None

---

### File: `db/migrations/versions/a8c3f1b2d9e7_create_proactive_tables.py`
* **Purpose**: Alembic revision script creating proactive outreach and events tables.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `upgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Creates `proactive_outreach_registry` and `proactive_events` tables.
  * **Function**: `downgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Drops proactive monitoring table layouts.
* **Constants**:
  * `revision`
  * `down_revision`
  * `branch_labels`
  * `depends_on`
* **Relationships**: None

---

### File: `db/migrations/versions/b1b3ec865383_create_translation_records_table.py`
* **Purpose**: Alembic revision script creating translation audit tables.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `upgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Creates the `translation_records` table and index constraints.
  * **Function**: `downgrade()`
    * **Parameters**: None
    * **Returns**: `None`
    * **Purpose**: Drops translation monitoring tables.
* **Constants**:
  * `revision`
  * `down_revision`
  * `branch_labels`
  * `depends_on`
* **Relationships**: None

---

### File: `docs/architecture.md`
* **Purpose**: Empty placeholder file for design documentation.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `docs/churn_formula.md`
* **Purpose**: Empty placeholder file for churn calculations.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `docs/dashboard_metrics.md`
* **Purpose**: Empty placeholder file for dashboard mappings.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `docs/event_contract.md`
* **Purpose**: Empty placeholder file for serialization standards.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `repositories/analytics_repository.py`
* **Purpose**: Read-Only Data Access Layer compiling metrics for dashboards and reports.
* **Classes**:
  * **Class**: `AnalyticsRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `get_agent_performance_metrics()`
      * `get_agent_csat_scores()`
      * `get_intent_volume_trends()`
      * `get_churn_segmentation()`
      * `get_refund_financials()`
    * **Purpose**: Compiles performance metrics, satisfaction trends, and intent frequencies.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `ticket_transcripts`, `feedback_signals`, `customer_support_profiles`
* **Relationships**:
  * Used By: `services/analytics/analytics_service.py`

---

### File: `repositories/churn_alert_repository.py`
* **Purpose**: Database operational ledger managing alert lifecycles and states.
* **Classes**:
  * **Class**: `ChurnAlertRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `create_alert()`
      * `get_open_alert()`
      * `get_pending_delivery_alerts()`
      * `mark_delivery_sent()`
      * `mark_delivery_failed()`
      * `acknowledge_alert()`
      * `resolve_alert()`
      * `get_by_alert_id()`
    * **Purpose**: Standard CRUD execution channel updating the operational alerts tables.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `churn_alerts`
* **Relationships**:
  * Used By: `services/alerts/alert_service.py`, `services/alerts/slack_notifier.py`, `services/processing/event_processor.py`

---

### File: `repositories/customer_event_repository.py`
* **Purpose**: Operational queue manager claiming and updating ingestion status records.
* **Classes**:
  * **Class**: `CRMEventRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `create_event()`
      * `claim_events_for_processing()`
      * `mark_done()`
      * `mark_failed()`
      * `mark_dead()`
      * `get_by_event_id()`
      * `replay_failed_events()`
      * `cleanup_dead_events()`
    * **Purpose**: Event-driven transaction channel claiming, executing, retrying, and pruning events.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `crm_events`
* **Relationships**:
  * Used By: `services/ingestion/event_claim_service.py`, `services/processing/event_processor.py`

---

### File: `repositories/customer_profile_repository.py`
* **Purpose**: Profile updater managing customer interaction frequencies and statuses.
* **Classes**:
  * **Class**: `CustomerProfileRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `upsert_profile_from_event()`
      * `get_profile()`
      * `update_churn_state()`
    * **Purpose**: Updates counts, preferences, sentiments, and scores for profile metadata.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `customer_support_profiles`
* **Relationships**:
  * Used By: `services/customer/profile_service.py`, `services/churn/churn_service.py`, `services/processing/event_processor.py`

---

### File: `repositories/feedback_repository.py`
* **Purpose**: Data Access Layer updating and polling satisfaction response records.
* **Classes**:
  * **Class**: `FeedbackRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `create_feedback()`
      * `get_by_ticket_id()`
      * `get_unprocessed_negative_feedback()`
      * `mark_processed_for_churn()`
      * `get_agent_feedback()`
    * **Purpose**: Interacts with the customer reviews database records.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `feedback_signals`
* **Relationships**: None

---

### File: `repositories/processed_event_repository.py`
* **Purpose**: Transaction deduplication registry tracking processed event status codes.
* **Classes**:
  * **Class**: `ProcessedEventRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `is_processed()`
      * `mark_processed()`
      * `mark_dead()`
      * `_mark_terminal()`
      * `get_by_event_id()`
    * **Purpose**: Low-level operational database controller enforcing transaction uniqueness.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `processed_events`
* **Relationships**:
  * Used By: `services/ingestion/idempotency_service.py`

---

### File: `repositories/transcript_repository.py`
* **Purpose**: Audit log ledger recorder logging flat message strings.
* **Classes**:
  * **Class**: `TranscriptRepository`
    * **Type**: Repository
    * **Methods**:
      * `__init__()`
      * `create_transcript()`
      * `get_by_ticket_id()`
      * `get_customer_history()`
      * `get_recent_negative_transcripts()`
    * **Purpose**: Operational channel recording flat transcripts and metrics variables.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Database Spec**:
  * **Database**: PostgreSQL (via SQLAlchemy)
  * **Tables Referenced**: `ticket_transcripts`
* **Relationships**:
  * Used By: `services/transcript/transcript_service.py`, `services/processing/event_processor.py`

---

### File: `schedulers/cleanup_dead_events.py`
* **Purpose**: Cron background service pruning old dead events.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `main()`
    * **Parameters**: None
    * **Returns**: None
    * **Purpose**: Instantiates connection session scope and deletes outdated DEAD events.
* **Constants**: None
* **Relationships**:
  * Consumes: `repositories/customer_event_repository.py`

---

### File: `schedulers/refresh_views.py`
* **Purpose**: Cron database management script executing materialized views refresh SQL.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `main()`
    * **Parameters**: None
    * **Returns**: None
    * **Purpose**: Automatically reconnects and executes REFRESH MATERIALIZED VIEW statements.
* **Constants**:
  * `MATERIALIZED_VIEWS`
* **Relationships**: None

---

### File: `schemas/alert.py`
* **Purpose**: Pydantic schema validation models for churn alerts.
* **Classes**:
  * **Class**: `AlertContext`
    * **Type**: Pydantic Model
    * **Fields**:
      * `customer_id : int`
      * `ticket_id : Optional[str] = None`
      * `customer_email : Optional[EmailStr] = None`
      * `tier : Literal["standard", "premium", "enterprise"] = "standard"`
      * `ltv : Decimal = Decimal("0.00")`
      * `source_agent : Optional[Literal["faq_agent", "refund_agent", "account_agent", "escalation_agent"]] = None`
    * **Purpose**: Customer tier and source variables mapping contextual parameters.
  * **Class**: `AlertPayload`
    * **Type**: Pydantic Model
    * **Fields**:
      * `alert_type : Literal["CHURN_RISK", "VIP_CHURN_RISK", "SECURITY_RISK", "LEGAL_RISK", "SLA_BREACH"]`
      * `severity : Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]`
      * `score : Decimal`
      * `reason : str`
      * `risk_reasons : List[str] = Field(default_factory=list)`
    * **Purpose**: Risk scoring properties tracking reason categories.
  * **Class**: `AlertRecord`
    * **Type**: Pydantic Model
    * **Methods**:
      * `serialize_datetime()`
      * `serialize_payload()`
      * `serialize_context()`
    * **Fields**:
      * `alert_id : str`
      * `context : AlertContext`
      * `payload : AlertPayload`
      * `alert_status : Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"] = "OPEN"`
      * `delivery_status : Literal["PENDING", "SENT", "FAILED"] = "PENDING"`
      * `acknowledged : bool = False`
      * `acknowledged_by : Optional[str] = None`
      * `acknowledged_at : Optional[datetime] = None`
      * `created_at : datetime`
    * **Purpose**: Complete envelope record containing the operational alert attributes.
* **Schemas / Models**:
  * `AlertContext`
  * `AlertPayload`
  * `AlertRecord`
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: Churn Alert repositories and services.

---

### File: `schemas/analytics.py`
* **Purpose**: Analytical point-in-time metrics models for business reports.
* **Classes**: None
* **Schemas / Models**:
  * **Schema**: `AgentPerformanceMetrics`
    * **Fields**:
      * `agent_name : Literal["faq_agent", "refund_agent", "account_agent", "escalation_agent"]`
      * `tickets_handled : int = 0`
      * `avg_resolution_time_ms : int = 0`
      * `escalation_rate : Decimal = Decimal("0.00")`
      * `failure_rate : Decimal = Decimal("0.00")`
      * `clarification_rate : Decimal = Decimal("0.00")`
    * **Purpose**: Holds speed, volume, and failure rates per specialist agent.
  * **Schema**: `IntentMetrics`
    * **Fields**:
      * `intent : str`
      * `ticket_count : int = 0`
      * `period_start : datetime`
      * `period_end : datetime`
    * **Purpose**: Ticket counts sorted by user queries.
  * **Schema**: `RefundMetrics`
    * **Fields**:
      * `total_refunds : int = 0`
      * `total_refund_amount : Decimal = Decimal("0.00")`
      * `refund_rejections : int = 0`
      * `human_review_count : int = 0`
      * `idempotent_replay_count : int = 0`
    * **Purpose**: Rejections and approval counts for transactions.
  * **Schema**: `FAQMetrics`
    * **Fields**:
      * `total_faq_resolved : int = 0`
      * `knowledge_gap_count : int = 0`
      * `clarification_count : int = 0`
      * `retrieval_failure_count : int = 0`
      * `containment_rate : Decimal = Decimal("0.00")`
    * **Purpose**: Gap tracking and resolved parameters for FAQs.
  * **Schema**: `AccountMetrics`
    * **Fields**:
      * `total_account_resolved : int = 0`
      * `security_escalation_count : int = 0`
      * `denial_count : int = 0`
      * `verification_failure_count : int = 0`
    * **Purpose**: Security reset and verification counts.
  * **Schema**: `EscalationMetrics`
    * **Fields**:
      * `total_escalations : int = 0`
      * `duplicate_suppressions : int = 0`
      * `human_review_count : int = 0`
      * `override_count : int = 0`
      * `escalation_failures : int = 0`
    * **Purpose**: Suppression and handoff execution counters.
  * **Schema**: `LanguageMetrics`
    * **Fields**:
      * `language : str`
      * `ticket_count : int = 0`
      * `translation_count : int = 0`
    * **Purpose**: Language usage breakdown metrics.
  * **Schema**: `ChurnDistributionMetrics`
    * **Fields**:
      * `low_count : int = 0`
      * `medium_count : int = 0`
      * `high_count : int = 0`
      * `critical_count : int = 0`
      * `computed_at : datetime`
    * **Purpose**: Customer base classification distribution segment counts.
  * **Schema**: `AnalyticsSnapshot`
    * **Fields**:
      * `snapshot_id : str`
      * `generated_at : datetime`
      * `agent_metrics : List[AgentPerformanceMetrics]`
      * `intent_metrics : List[IntentMetrics]`
      * `refund_metrics : Optional[RefundMetrics] = None`
      * `faq_metrics : Optional[FAQMetrics] = None`
      * `account_metrics : Optional[AccountMetrics] = None`
      * `escalation_metrics : Optional[EscalationMetrics] = None`
      * `language_metrics : List[LanguageMetrics]`
      * `churn_distribution : ChurnDistributionMetrics`
    * **Purpose**: Consolidated analytics tracking data.
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: analytics repositories and services.

---

### File: `schemas/churn.py`
* **Purpose**: Calculations payload mapping customer activity trends to risk factors.
* **Classes**: None
* **Schemas / Models**:
  * **Schema**: `ChurnSignalInput`
    * **Fields**:
      * `customer_id : int`
      * `ltv : Decimal = Decimal("0.00")`
      * `total_tickets : int`
      * `negative_ticket_count : int = 0`
      * `unresolved_ticket_count : int = 0`
      * `repeat_negative_count : int = 0`
      * `repeat_escalation_count : int = 0`
      * `duplicate_request_count : int = 0`
      * `last_sentiment : Optional[str] = None`
      * `current_sentiment : Optional[str] = None`
      * `sentiment_trend : Literal["improving", "stable", "declining"] = "stable"`
      * `days_since_last_ticket : int = 0`
      * `security_incident : bool = False`
      * `legal_incident : bool = False`
      * `high_value_customer : bool = False`
    * **Purpose**: Flat parameters feeding the deterministic calculation.
  * **Schema**: `ChurnComputationBreakdown`
    * **Fields**:
      * `negative_ticket_score : Decimal = Decimal("0.00")`
      * `unresolved_score : Decimal = Decimal("0.00")`
      * `sentiment_score : Decimal = Decimal("0.00")`
      * `escalation_score : Decimal = Decimal("0.00")`
      * `inactivity_score : Decimal = Decimal("0.00")`
      * `security_score : Decimal = Decimal("0.00")`
      * `legal_score : Decimal = Decimal("0.00")`
      * `vip_multiplier_applied : Decimal = Decimal("1.00")`
      * `raw_score : Decimal = Decimal("0.00")`
      * `final_score : Decimal`
    * **Purpose**: Explainable calculation receipts listing score components.
  * **Schema**: `ChurnAssessment`
    * **Fields**:
      * `customer_id : int`
      * `churn_score : Decimal`
      * `churn_level : Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]`
      * `risk_reasons : List[str]`
      * `breakdown : ChurnComputationBreakdown`
      * `computed_at : datetime`
    * **Purpose**: Complete assessment outcome decision record.
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: ChurnEngine and alert services.

---

### File: `schemas/crm_event.py`
* **Purpose**: Canonical contract models standardizing ingestion payloads.
* **Classes**: None
* **Schemas / Models**:
  * **Schema**: `EventMetadata`
    * **Fields**:
      * `event_id : str`
      * `event_type : str`
      * `source_agent : str`
      * `schema_version : str = "1.0.0"`
      * `created_at : datetime`
    * **Purpose**: System properties identifying tracking details.
  * **Schema**: `TicketMetadata`
    * **Fields**:
      * `ticket_id : str`
      * `workflow_id : Optional[str] = None`
      * `trace_id : Optional[str] = None`
      * `channel : str = "web"`
    * **Purpose**: Tracking identifiers maps.
  * **Schema**: `CustomerMetadata`
    * **Fields**:
      * `customer_id : int`
      * `customer_email : Optional[EmailStr] = None`
      * `tier : str = "standard"`
      * `ltv : Decimal = Decimal("0.00")`
      * `language : str = "en"`
    * **Purpose**: Basic profile variables mappings.
  * **Schema**: `ResolutionMetadata`
    * **Fields**:
      * `status : Literal["resolved", "escalated", "denied", "failed", "clarification_required", "duplicate_suppressed", "human_review_required"]`
      * `resolution_type : str`
      * `resolution_message : Optional[str] = None`
      * `resolved_by : str`
      * `time_to_resolution_ms : Optional[int] = None`
    * **Purpose**: Outcome values mapping status details.
  * **Schema**: `RiskMetadata`
    * **Fields**:
      * `escalated : bool = False`
      * `security_flag : bool = False`
      * `legal_flag : bool = False`
      * `human_review_required : bool = False`
      * `risk_level : Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"`
    * **Purpose**: Incident flag statuses.
  * **Schema**: `FinancialMetadata`
    * **Fields**:
      * `refund_amount : Optional[Decimal] = None`
      * `currency : Optional[str] = "USD"`
      * `transaction_id : Optional[str] = None`
    * **Purpose**: Refund values mappings.
  * **Schema**: `DecisionMetadata`
    * **Fields**:
      * `decision_code : Optional[str] = None`
      * `decision_reason : Optional[str] = None`
      * `verification_level : Optional[str] = None`
      * `review_required : bool = False`
      * `human_override : bool = False`
    * **Purpose**: Policy audit codes.
  * **Schema**: `AnalyticsMetadata`
    * **Fields**:
      * `intent : Optional[str] = None`
      * `issue_tags : List[str]`
      * `priority : Optional[str] = None`
      * `sla_hours : Optional[int] = None`
      * `feedback : Optional[str] = None`
      * `sentiment_start : Optional[str] = None`
      * `sentiment_end : Optional[str] = None`
    * **Purpose**: Sentiment trends.
  * **Schema**: `ConversationMetadata`
    * **Fields**:
      * `messages : List[Dict[str, Any]]`
      * `agents_involved : List[str]`
      * `original_message : Optional[str] = None`
      * `translated_message : Optional[str] = None`
    * **Purpose**: Message records.
  * **Schema**: `CRMResolvedEvent`
    * **Fields**:
      * `event : EventMetadata`
      * `ticket : TicketMetadata`
      * `customer : CustomerMetadata`
      * `resolution : ResolutionMetadata`
      * `risk : RiskMetadata`
      * `financial : Optional[FinancialMetadata] = None`
      * `decision : Optional[DecisionMetadata] = None`
      * `analytics : Optional[AnalyticsMetadata] = None`
      * `conversation : Optional[ConversationMetadata] = None`
    * **Purpose**: Canonical wrapper normalizing specialists outputs.
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: all adapters, processors, executors, and repositories.

---

### File: `schemas/customer_profile.py`
* **Purpose**: Data structures updating historical profiles.
* **Classes**: None
* **Schemas / Models**:
  * **Schema**: `SentimentProfile`
    * **Fields**:
      * `last_sentiment : Optional[str] = None`
      * `sentiment_history : List[str]`
      * `negative_sentiment_count : int = 0`
    * **Purpose**: Satisfaction history fields.
  * **Schema**: `ChurnMetrics`
    * **Fields**:
      * `churn_score : Decimal = Decimal("0.00")`
      * `churn_level : Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"`
      * `churn_last_updated : datetime`
    * **Purpose**: Risk score parameters.
  * **Schema**: `CustomerProfile`
    * **Fields**:
      * `customer_id : int`
      * `customer_email : Optional[EmailStr] = None`
      * `tier : Literal["standard", "premium", "enterprise"] = "standard"`
      * `ltv : Decimal = Decimal("0.00")`
      * `total_tickets : int = 0`
      * `total_faq_tickets : int = 0`
      * `total_refund_tickets : int = 0`
      * `total_account_tickets : int = 0`
      * `total_escalations : int = 0`
      * `total_denials : int = 0`
      * `total_failures : int = 0`
      * `total_clarifications : int = 0`
      * `total_duplicate_suppressions : int = 0`
      * `repeat_negative_count : int = 0`
      * `repeat_escalation_count : int = 0`
      * `duplicate_request_count : int = 0`
      * `negative_ticket_count : int = 0`
      * `sentiment_profile : SentimentProfile`
      * `churn_intelligence : ChurnMetrics`
      * `issue_frequency : Dict[str, int]`
      * `agent_interaction_frequency : Dict[str, int]`
      * `languages_used : List[str]`
      * `preferred_language : str = "en"`
      * `first_seen_at : datetime`
      * `last_ticket_at : Optional[datetime] = None`
      * `updated_at : datetime`
      * `created_at : datetime`
    * **Properties**:
      * `issue_tags` (getter/setter)
      * `agent_interactions` (getter/setter)
    * **Purpose**: Customer database profile compilation models.
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: profile updates services and repositories.

---

### File: `schemas/transcript.py`
* **Purpose**: Models mapping the conversation audit transcripts.
* **Classes**: None
* **Schemas / Models**:
  * **Schema**: `MessageMetadata`
    * **Fields**:
      * `language : Optional[str] = None`
      * `translated : Optional[bool] = None`
      * `tool_used : Optional[str] = None`
    * **Purpose**: Translation tracker tags.
  * **Schema**: `MessageEntry`
    * **Fields**:
      * `role : Literal["customer", "faq_agent", "refund_agent", "account_agent", "escalation_agent", "human_agent", "system"]`
      * `content : str`
      * `timestamp : datetime`
      * `metadata : Optional[MessageMetadata] = None`
    * **Purpose**: Single message text entry log details.
  * **Schema**: `ResolutionSummary`
    * **Fields**:
      * `status : Literal["resolved", "escalated", "denied", "failed", "clarification_required", "duplicate_suppressed", "human_review_required"]`
      * `resolution_type : str`
      * `resolution_message : Optional[str] = None`
      * `resolved_by : str`
      * `time_to_resolution_ms : Optional[int] = None`
    * **Purpose**: Detailed resolution state wrapper.
  * **Schema**: `TranscriptRecord`
    * **Fields**:
      * `id : Optional[int] = None`
      * `schema_version : str = "1.0.0"`
      * `ticket_id : str`
      * `customer_id : int`
      * `source_agent : Literal["faq_agent", "refund_agent", "account_agent", "escalation_agent"]`
      * `workflow_id : Optional[str] = None`
      * `trace_id : Optional[str] = None`
      * `channel : Optional[str] = None`
      * `messages : List[MessageEntry]`
      * `agents_involved : List[Literal["supervisor", "triage_agent", "faq_agent", "refund_agent", "account_agent", "escalation_agent", "human_agent"]]`
      * `original_message : Optional[str] = None`
      * `translated_message : Optional[str] = None`
      * `intent : Optional[str] = None`
      * `priority : Optional[str] = None`
      * `sentiment_start : Optional[str] = None`
      * `sentiment_end : Optional[str] = None`
      * `issue_tags : List[str]`
      * `resolution : ResolutionSummary`
      * `feedback : Optional[Literal["thumbs_up", "thumbs_down"]] = None`
      * `created_at : datetime`
    * **Properties**:
      * `status` (getter/setter)
      * `resolution_type` (getter/setter)
      * `resolution_message` (getter/setter)
      * `resolved_by` (getter/setter)
      * `time_to_resolution_ms` (getter/setter)
    * **Purpose**: Audit transcript record container.
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Consumed by: transcript repositories and services.

---

### File: `scripts/replay_failed_events.py`
* **Purpose**: System admin shell script requeuing failed CRM events to NEW state.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `main()`
    * **Parameters**: None
    * **Returns**: None
    * **Purpose**: Instantiates connection session and invokes queue event replayer methods.
* **Constants**: None
* **Relationships**:
  * Consumes: `repositories/customer_event_repository.py`

---

### File: `scripts/run_refresh_scheduler.py`
* **Purpose**: Empty placeholder script for refreshing scheduler execution.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `scripts/run_worker.py`
* **Purpose**: Background daemon launcher script loading engines and initializing processing loops.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**:
  * **Function**: `build_claim_service()`
    * **Parameters**: `session`
    * **Returns**: `EventClaimService`
    * **Purpose**: Instantiates claim tracker services.
  * **Function**: `build_processor()`
    * **Parameters**: `session`
    * **Returns**: `EventProcessor`
    * **Purpose**: Wires and instantiates the complete transactional queue orchestrator.
  * **Function**: `main()`
    * **Parameters**: None
    * **Returns**: None
    * **Purpose**: Resolves engine dependencies, prepares shutdown handlers, and starts daemon loops.
* **Constants**: None
* **Relationships**:
  * Consumes: `services/ingestion/event_consumer.py`, `services/processing/event_processor.py`

---

### File: `services/alerts/alert_service.py`
* **Purpose**: Evaluates risk assessment metrics and determines whether alerts are suppressed.
* **Classes**:
  * **Class**: `AlertService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `create_alert_if_needed()`
      * `_is_alert_required()`
      * `_determine_alert_type()`
      * `_is_suppressed()`
    * **Purpose**: Evaluates risk assessments to stage alerts when severity levels breach parameters.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `ChurnAlertRepository`
* **Relationships**:
  * Used By: `services/processing/pipeline_executor.py`

---

### File: `services/alerts/slack_notifier.py`
* **Purpose**: Dispatches formatted notifications to Slack/Console loggers.
* **Classes**:
  * **Class**: `SlackNotifier`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `dispatch_alert()`
      * `_build_alert_message()`
      * `_send()`
      * `_mark_delivery_success()`
      * `_mark_delivery_failed()`
    * **Purpose**: Formats alert models and manages external delivery flags.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `ChurnAlertRepository`
* **Relationships**: None

---

### File: `services/analytics/analytics_service.py`
* **Purpose**: Resolves analytical parameters into strict dashboard snapshot data blocks.
* **Classes**:
  * **Class**: `AnalyticsService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `generate_dashboard_snapshot()`
      * `_calculate_rate()`
    * **Purpose**: Translates metrics datasets to populate system dashboard snapshot fields.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `AnalyticsRepository`
* **Relationships**:
  * Used By: `services/analytics/metrics_aggregator.py`

---

### File: `services/analytics/metrics_aggregator.py`
* **Purpose**: Compiles high-level corporate KPIs and ranks agent performance leaderboard indexes.
* **Classes**:
  * **Class**: `MetricsAggregator`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `generate_executive_kpis()`
      * `_calculate_total_volume()`
      * `_determine_top_issue()`
      * `_calculate_risk_exposure()`
      * `_build_agent_leaderboard()`
    * **Purpose**: Organizes counts, ratios, rankings, and snapshots into executive KPI dictionaries.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `AnalyticsService`
* **Relationships**: None

---

### File: `services/churn/churn_engine.py`
* **Purpose**: Deterministic math calculator scoring customer churn risk parameters.
* **Classes**:
  * **Class**: `ChurnEngine`
    * **Type**: Utility
    * **Methods**:
      * `__init__()`
      * `calculate_churn_risk()`
      * `_calculate_negative_ticket_score()`
      * `_calculate_escalation_score()`
      * `_calculate_sentiment_score()`
      * `_calculate_inactivity_score()`
      * `_apply_vip_multiplier()`
      * `_determine_churn_level()`
      * `_generate_risk_reasons()`
    * **Purpose**: Parses interaction metrics to output structured ChurnAssessments.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `MAX_SCORE`
  * `WEIGHT_FAILURE`
  * `WEIGHT_ESCALATION`
  * `WEIGHT_DENIAL`
  * `VIP_MULTIPLIER`
  * `INACTIVITY_THRESHOLD_DAYS`
* **Relationships**:
  * Used By: `services/churn/churn_service.py`, `services/processing/event_processor.py`

---

### File: `services/churn/churn_service.py`
* **Purpose**: Fetches profile data and delegates scoring to the ChurnEngine.
* **Classes**:
  * **Class**: `ChurnService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `analyze_customer_risk()`
    * **Purpose**: Gathers relational customer database inputs to execute mathematical scoring operations.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `ChurnEngine`, `CustomerProfileRepository`
* **Relationships**:
  * Used By: `services/processing/pipeline_executor.py`

---

### File: `services/customer/issue_tag_service.py`
* **Purpose**: Empty placeholder service for processing issue tags.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `services/customer/language_service.py`
* **Purpose**: Empty placeholder service for customer languages.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `services/customer/profile_service.py`
* **Purpose**: Validates customer profiles and coordinates CRM upsert logic.
* **Classes**:
  * **Class**: `ProfileService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `update_customer_profile()`
      * `_validate_event()`
    * **Purpose**: Coordinates validation checks prior to committing customer updates.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `CustomerProfileRepository`
* **Relationships**:
  * Used By: `services/processing/pipeline_executor.py`

---

### File: `services/customer/sentiment_service.py`
* **Purpose**: Empty placeholder service for satisfaction/sentiment analytics.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Relationships**: None

---

### File: `services/ingestion/event_claim_service.py`
* **Purpose**: Orchestrates worker claims and recovers stale PROCESSING status records.
* **Classes**:
  * **Class**: `EventClaimService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `claim_events()`
      * `release_stale_claims()`
    * **Purpose**: Claims items from the distributed database queue and recovers stale claims.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `CRMEventRepository`
* **Relationships**:
  * Used By: `services/ingestion/event_consumer.py`, `scripts/run_worker.py`

---

### File: `services/ingestion/event_consumer.py`
* **Purpose**: Distributed poll loop daemon polling the event queue and forwarding transactions.
* **Classes**:
  * **Class**: `CRMEventConsumer`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `_handle_shutdown()`
      * `start()`
      * `_claim_batch()`
      * `_process_single_event()`
      * `_mark_poison_pill_dead()`
      * `_run_maintenance_if_needed()`
    * **Purpose**: Manages background worker execution and recovers abandoned operations.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `sessionmaker`, `EventProcessor` (factory), `EventClaimService` (factory)
* **Relationships**:
  * Used By: `scripts/run_worker.py`

---

### File: `services/ingestion/idempotency_service.py`
* **Purpose**: Enforces transaction deduplication checking and registers terminal state keys.
* **Classes**:
  * **Class**: `IdempotencyService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `is_duplicate_event()`
      * `mark_success()`
      * `mark_dead()`
    * **Purpose**: Verifies incoming identifiers to skip double-processing.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `ProcessedEventRepository`
* **Relationships**:
  * Used By: `services/processing/event_processor.py`, `scripts/run_worker.py`

---

### File: `services/processing/event_processor.py`
* **Purpose**: Main transactional pipeline coordinating router checks and commits.
* **Classes**:
  * **Class**: `EventProcessor`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `process_event()`
      * `_handle_alerts()`
    * **Purpose**: Orchestrates the pipeline stages of transcript log creation, customer database updates, and alert evaluation.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `Session`, `EventRouter`, `IdempotencyService`, `ChurnEngine`, `CRMEventRepository`, `TranscriptRepository`, `CustomerProfileRepository`, `ChurnAlertRepository`
* **Relationships**:
  * Used By: `services/ingestion/event_consumer.py`, `scripts/run_worker.py`

---

### File: `services/processing/event_router.py`
* **Purpose**: Evaluates routing criteria and generates deterministic ExecutionPlans.
* **Classes**:
  * **Class**: `ExecutionPlan`
    * **Type**: Dataclass
    * **Fields**:
      * `route : PipelineRoute`
      * `is_terminal : bool`
      * `persist_transcript : bool`
      * `update_profile : bool`
      * `run_churn_analysis : bool`
      * `generate_alerts : bool`
      * `failure_reason : str | None = None`
    * **Purpose**: Holds execution directives for processing events.
  * **Class**: `EventRouter`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `build_processing_plan()`
      * `_resolve_pipeline()`
      * `_validate_route()`
      * `_is_terminal_event()`
      * `_requires_transcript_persistence()`
      * `_requires_profile_update()`
      * `_requires_churn_analysis()`
      * `_requires_alert_generation()`
      * `_handle_unknown_route()`
    * **Purpose**: Stateless dispatcher classifying events based on agent properties.
* **Schemas / Models**: None
* **Enums**:
  * **Enum**: `PipelineRoute`
    * **Values**:
      * `FAQ` = `"faq_pipeline"`
      * `REFUND` = `"refund_pipeline"`
      * `ACCOUNT` = `"account_pipeline"`
      * `ESCALATION` = `"escalation_pipeline"`
      * `DEAD_LETTER` = `"dead_letter_pipeline"`
      * `UNKNOWN` = `"unknown_pipeline"`
    * **Purpose**: Routing destination identifiers.
* **Functions**: None
* **Constants**: None
* **Relationships**:
  * Used By: `services/processing/event_processor.py`, `scripts/run_worker.py`

---

### File: `services/processing/pipeline_executor.py`
* **Purpose**: Sequentially triggers enabled workflow steps for a processing plan.
* **Classes**:
  * **Class**: `PipelineExecutor`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `execute_plan()`
    * **Purpose**: Sequentially executes the pipeline steps specified by the plan.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `TranscriptService`, `ProfileService`, `ChurnService`, `AlertService`
* **Relationships**:
  * Used By: `scripts/run_worker.py`

---

### File: `services/transcript/transcript_service.py`
* **Purpose**: Manages event integrity verification and delegates transcript logging.
* **Classes**:
  * **Class**: `TranscriptService`
    * **Type**: Service
    * **Methods**:
      * `__init__()`
      * `create_transcript()`
      * `_validate_event()`
      * `get_customer_history()`
      * `get_ticket_transcript()`
    * **Purpose**: Orchestrates validation and persistence for transcripts.
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**: None
* **Service Details**:
  * **Dependencies**: `TranscriptRepository`
* **Relationships**:
  * Used By: `services/processing/pipeline_executor.py`, `scripts/run_worker.py`

---

### File: `tests/fixtures/account_payloads.py`
* **Purpose**: Holds static dictionary payloads simulating Account Agent outputs.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `ACCOUNT_PASSWORD_RESET_OUTPUT`
  * `ACCOUNT_ESCALATION_OUTPUT`
  * `ACCOUNT_DENIED_OUTPUT`
* **Relationships**: Consumed by test suites.

---

### File: `tests/fixtures/common.py`
* **Purpose**: Defines shared customer context properties for testing workflows.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `GLOBAL_CONTEXT`
* **Relationships**: Consumed by test suites.

---

### File: `tests/fixtures/escalation_payloads.py`
* **Purpose**: Holds static dictionary payloads simulating Escalation Agent outputs.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `ESCALATION_SUCCESS_OUTPUT`
  * `ESCALATION_DUPLICATE_OUTPUT`
  * `ESCALATION_REVIEW_OUTPUT`
  * `ESCALATION_FAILED_OUTPUT`
* **Relationships**: Consumed by test suites.

---

### File: `tests/fixtures/faq_payloads.py`
* **Purpose**: Holds static dictionary payloads simulating FAQ Agent outputs.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `FAQ_SUCCESS_OUTPUT`
  * `FAQ_CLARIFICATION_OUTPUT`
  * `FAQ_KNOWLEDGE_GAP_OUTPUT`
* **Relationships**: Consumed by test suites.

---

### File: `tests/fixtures/refund_payloads.py`
* **Purpose**: Holds static dictionary payloads simulating Refund Agent outputs.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None
* **Constants**:
  * `REFUND_AUTO_APPROVE_OUTPUT`
  * `REFUND_HUMAN_REVIEW_OUTPUT`
  * `REFUND_REJECTED_OUTPUT`
  * `REFUND_IDEMPOTENT_OUTPUT`
* **Relationships**: Consumed by test suites.

---

### File: `tests/unit/test_adapters.py`
* **Purpose**: Unit tests verifying special agent adapters transform data correctly.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/unit/test_churn_engine.py`
* **Purpose**: Unit tests verifying deterministic math scoring formulas.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/unit/test_event_claiming.py`
* **Purpose**: Unit tests verifying queue operations, locks, and timeouts.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/unit/test_idempotency.py`
* **Purpose**: Unit tests verifying duplicate event prevention filters.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/unit/test_profile_updates.py`
* **Purpose**: Unit tests verifying customer profile counter updates.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/integration/test_alert_flow.py`
* **Purpose**: Integration tests verifying alert evaluation, suppression, and Outbox staging.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/integration/test_customer_updates.py`
* **Purpose**: Integration tests verifying customer profile database updates.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/integration/test_end_to_end_crm_flow.py`
* **Purpose**: End-to-end integration tests verifying complete pipeline execution flows.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/integration/test_event_pipeline.py`
* **Purpose**: Integration tests verifying router ExecutionPlans and pipeline stages.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

### File: `tests/integration/test_transcript_persistence.py`
* **Purpose**: Integration tests verifying transcript persistence databases.
* **Classes**: None
* **Schemas / Models**: None
* **Enums**: None
* **Functions**: None (contains test execution functions)
* **Constants**: None
* **Relationships**: None

---

## Section 3: Folder Summary

### Folder Purpose
The `demorepo` folder implements the CRM background worker component of the Customer Support AI platform. It ingests resolved customer interaction event payloads from specialized agents (FAQ, Refund, Account, Escalation), parses them through custom Adapters into standard schemas, logs immutable transcripts, tracks satisfaction reviews, maintains historical customer profiles, and deterministically calculates customer churn risk metrics to raise alerts for high-risk accounts.

### Files Included
All files discovered inside the codebase directory are listed sequentially below:
* `config.py`
* `constants.py`
* `main.py`
* `alembic.ini`
* `adapters/account_adapter.py`
* `adapters/base_adapter.py`
* `adapters/escalation_adapter.py`
* `adapters/faq_adapter.py`
* `adapters/refund_adapter.py`
* `dashboards/metabase_setup.md`
* `db/base.py`
* `db/connection.py`
* `db/migrations/env.py`
* `db/migrations/versions/5bfb7b38709d_create_crm_tables.py`
* `db/migrations/versions/a8c3f1b2d9e7_create_proactive_tables.py`
* `db/migrations/versions/b1b3ec865383_create_translation_records_table.py`
* `db/models/churn_alert_model.py`
* `db/models/crm_event_model.py`
* `db/models/customer_profile_model.py`
* `db/models/feedback_model.py`
* `db/models/processed_event_model.py`
* `db/models/transcript_model.py`
* `docs/architecture.md`
* `docs/churn_formula.md`
* `docs/dashboard_metrics.md`
* `docs/event_contract.md`
* `repositories/analytics_repository.py`
* `repositories/churn_alert_repository.py`
* `repositories/customer_event_repository.py`
* `repositories/customer_profile_repository.py`
* `repositories/feedback_repository.py`
* `repositories/processed_event_repository.py`
* `repositories/transcript_repository.py`
* `schedulers/cleanup_dead_events.py`
* `schedulers/refresh_views.py`
* `schemas/alert.py`
* `schemas/analytics.py`
* `schemas/churn.py`
* `schemas/crm_event.py`
* `schemas/customer_profile.py`
* `schemas/transcript.py`
* `scripts/replay_failed_events.py`
* `scripts/run_refresh_scheduler.py`
* `scripts/run_worker.py`
* `services/alerts/alert_service.py`
* `services/alerts/slack_notifier.py`
* `services/analytics/analytics_service.py`
* `services/analytics/metrics_aggregator.py`
* `services/churn/churn_engine.py`
* `services/churn/churn_service.py`
* `services/customer/issue_tag_service.py`
* `services/customer/language_service.py`
* `services/customer/profile_service.py`
* `services/customer/sentiment_service.py`
* `services/ingestion/event_claim_service.py`
* `services/ingestion/event_consumer.py`
* `services/ingestion/idempotency_service.py`
* `services/processing/event_processor.py`
* `services/processing/event_router.py`
* `services/processing/pipeline_executor.py`
* `services/transcript/transcript_service.py`

### Main Components
* **Repositories**:
  * `AnalyticsRepository`
  * `ChurnAlertRepository`
  * `CRMEventRepository`
  * `CustomerProfileRepository`
  * `FeedbackRepository`
  * `ProcessedEventRepository`
  * `TranscriptRepository`
* **Services**:
  * `AlertService`
  * `SlackNotifier`
  * `AnalyticsService`
  * `MetricsAggregator`
  * `ChurnService`
  * `ProfileService`
  * `EventClaimService`
  * `CRMEventConsumer`
  * `IdempotencyService`
  * `EventProcessor`
  * `PipelineExecutor`
  * `TranscriptService`
* **Schemas**:
  * `AlertContext`, `AlertPayload`, `AlertRecord`
  * `AgentPerformanceMetrics`, `IntentMetrics`, `RefundMetrics`, `FAQMetrics`, `AccountMetrics`, `EscalationMetrics`, `LanguageMetrics`, `ChurnDistributionMetrics`, `AnalyticsSnapshot`
  * `ChurnSignalInput`, `ChurnComputationBreakdown`, `ChurnAssessment`
  * `EventMetadata`, `TicketMetadata`, `CustomerMetadata`, `ResolutionMetadata`, `RiskMetadata`, `FinancialMetadata`, `DecisionMetadata`, `AnalyticsMetadata`, `ConversationMetadata`, `CRMResolvedEvent`
  * `SentimentProfile`, `ChurnMetrics`, `CustomerProfile`
  * `MessageMetadata`, `MessageEntry`, `ResolutionSummary`, `TranscriptRecord`
* **Enums**:
  * `PipelineRoute`
* **Utilities**:
  * `BaseAdapter`, `AccountAdapter`, `EscalationAdapter`, `FAQAdapter`, `RefundAdapter`
  * `ChurnEngine`
* **Graphs**:
  * None

### Input / Output
* **Input**:
  * Raw dictionary agent outputs from FAQ, Refund, Account, or Escalation agents (containing tickets details, customer properties, decisions, or customer satisfaction reviews).
* **Output**:
  * Canonical `CRMResolvedEvent` formats stored as database transcripts, updated customer profile counts, churn severity records, and staged operational alerts.

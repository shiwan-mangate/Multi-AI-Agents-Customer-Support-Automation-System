# Layer 2 Proactive Agent - Codebase Inventory

## Section 1: Folder Structure

```
layer_2_proactive_agent/
│
├── main.py
├── proactive_agent_playground.ipynb
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── constants.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   ├── base.py
│   ├── session.py
│   └── model/
│       ├── __init__.py
│       ├── proactive_event_record.py
│       └── proactive_outreach_record.py
│
├── schemas/
│   ├── __init__.py
│   ├── enums.py
│   ├── proactive_state.py
│   ├── proactive_output.py
│   ├── risk_assessment.py
│   ├── signal_assessment.py
│   ├── signal.py
│   ├── outreach_decision.py
│   ├── outreach_message.py
│   └── escalation_handoff.py
│
├── services/
│   ├── __init__.py
│   ├── signal_detection_service.py
│   ├── risk_engine.py
│   ├── outreach_decision_service.py
│   ├── message_generation_service.py
│   ├── escalation_service.py
│   ├── suppression_service.py
│   └── proactive_orchestrator.py
│
├── repositories/
│   ├── __init__.py
│   ├── customer_profile_repository.py
│   ├── proactive_outreach_repository.py
│   ├── proactive_event_repository.py
│   └── transcript_repository.py
│
├── nodes/
│   ├── __init__.py
│   ├── validate_signal_node.py
│   ├── customer_context_node.py
│   ├── suppression_gate_node.py
│   ├── signal_analysis_node.py
│   ├── risk_scoring_node.py
│   ├── outreach_decision_node.py
│   ├── message_generation_node.py
│   ├── escalation_handoff_node.py
│   └── response_node.py
│
├── graph/
│   ├── __init__.py
│   ├── proactive_graph.py
│   ├── routers.py
│   └── state_factory.py
│
├── prompts/
│   ├── __init__.py
│   ├── base_prompt.py
│   ├── high_churn_prompt.py
│   ├── inactive_customer_prompt.py
│   ├── negative_experience_prompt.py
│   └── vip_retention_prompt.py
│
├── adapters/
│   ├── __init__.py
│   └── proactive_adapter.py
│
├── integration/
│   ├── __init__.py
│   ├── crm_integration.py
│   └── escalation_integration.py
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── exceptions.py
│   ├── id_generator.py
│   ├── datetime_utils.py
│   └── score_utils.py
│
├── evaluation/
│   ├── __init__.py
│   ├── eval_runner.py
│   ├── metrics.py
│   └── datasets/
│       ├── churn_cases.json
│       ├── proactive_negative_cases.json
│       ├── proactive_positive_cases.json
│       └── vip_cases.json
│
└── tests/
    ├── conftest.py
    ├── fixtures/
    │   ├── churn_fixtures.py
    │   ├── customer_profiles.py
    │   ├── signal_fixtures.py
    │   └── transcript_fixtures.py
    ├── unit/
    │   ├── test_adapter.py
    │   ├── test_customer_context_node.py
    │   ├── test_escalation_handoff_node.py
    │   ├── test_message_generation_node.py
    │   ├── test_outreach_decision_node.py
    │   ├── test_responce_node.py
    │   ├── test_risk_engine.py
    │   ├── test_risk_scoring_node.py
    │   ├── test_signal_analysis_node.py
    │   ├── test_suppression_gate_node.py
    │   ├── test_suppression_service.py
    │   └── test_validate_signal_node.py
    ├── integration/
    │   ├── test_crm_event_creation.py
    │   ├── test_escalation_contract.py
    │   ├── test_full_escalation_flow.py
    │   ├── test_full_outreach_flow.py
    │   └── test_outreach_registry.py
    └── e2e/
        └── test_end_to_end_proactive_agent.py
```

---

## Section 2: File Analysis

### File: config/settings.py

**Purpose**

PostgreSQL database connection configuration and singleton settings instance.

**Classes**

Class: Settings
Type: Configuration Class

Methods:
- db_user (property)
- db_pass (property)
- db_host (property)
- db_port (property)
- db_name (property)

Purpose:
Centralizes database credentials and connection parameters. Creates singleton `settings` instance for application-wide use.

**Constants**

```
db_user = "postgres"
db_pass = "pass9325"
db_host = "localhost"
db_port = 5432
db_name = "customer_support_ai"
```

---

### File: database/base.py

**Purpose**

SQLAlchemy declarative base class for all ORM models and database table definitions.

**Classes**

Class: Base
Type: Utility / ORM Base

Methods:
None (pure registration blueprint)

Purpose:
Master registry for all PostgreSQL table metadata. All ORM models inherit from this to enable Alembic migrations.

---

### File: database/session.py

**Purpose**

PostgreSQL database connection pooling, session factory, and dependency injection.

**Functions**

Function: get_db()

Parameters:
None

Returns:
Generator[Session, None, None]

Purpose:
Context manager for safe database session handling in FastAPI/request cycles.

**Constants**

```
DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
```

**Relationships**

Produces:
- SessionLocal (scoped session factory)
- engine (SQLAlchemy create_engine with connection pooling)

---

### File: database/model/proactive_event_record.py

**Purpose**

ORM model for audit and analytics record of completed proactive workflows.

**Classes**

Class: ProactiveEventRecord
Type: SQLAlchemy ORM Model

Methods:
None (pure data model)

Fields:
- id: str (UUID, primary key)
- workflow_id: str (varchar 100, indexed)
- signal_id: str (varchar 100)
- customer_id: int (bigint, indexed)
- signal_type: str (varchar 100, indexed)
- risk_level: str (varchar 50)
- decision: str (varchar 50)
- crm_event_id: str (varchar 100)
- created_at: datetime (timezone-aware UTC, indexed)

Purpose:
Tracks all completed proactive workflows for auditing and analytics. Contains three indexed columns for fast querying by customer, signal type, and creation date.

**Database**

Database:
- PostgreSQL

Tables Referenced:
- proactive_events

Indexes:
- idx_proactive_events_customer (customer_id)
- idx_proactive_events_signal (signal_type)
- idx_proactive_events_created (created_at)

---

### File: database/model/proactive_outreach_record.py

**Purpose**

ORM model for suppression registry and idempotency tracking to prevent duplicate proactive outreach.

**Classes**

Class: ProactiveOutreachRecord
Type: SQLAlchemy ORM Model

Methods:
None (pure data model)

Fields:
- id: str (UUID, primary key)
- workflow_id: str (varchar 100)
- signal_id: str (varchar 100)
- customer_id: int (bigint, indexed)
- signal_type: str (varchar 100, indexed)
- decision: str (varchar 50)
- status: str (varchar 50)
- created_at: datetime (timezone-aware UTC)
- expires_at: datetime (timezone-aware UTC, indexed)

Purpose:
Suppression/cooldown registry. Prevents duplicate outreach to customers within configured suppression windows per signal type.

**Database**

Database:
- PostgreSQL

Tables Referenced:
- proactive_outreach_registry

Indexes:
- idx_proactive_customer_signal (customer_id, signal_type)
- idx_proactive_expires_at (expires_at)

---

### File: schemas/enums.py

**Purpose**

Enumeration contracts for signals, risk levels, outreach actions, sources, and workflow statuses.

**Enums**

Enum: SignalType

Values:
- INACTIVE_CUSTOMER
- HIGH_CHURN_RISK
- RECENT_NEGATIVE_EXPERIENCE
- VIP_RETENTION_RISK

Purpose:
Supported proactive detection signal categories.

Enum: RiskLevel

Values:
- LOW
- MEDIUM
- HIGH
- CRITICAL

Purpose:
Risk severity levels used across assessment and decision nodes.

Enum: OutreachAction

Values:
- NO_ACTION
- OUTREACH
- ESCALATE

Purpose:
Final workflow decision outcomes from proactive evaluation.

Enum: SignalSource

Values:
- CRM
- STRIPE
- SHOPIFY
- STATUS_PAGE
- SYSTEM

Purpose:
Origin/source of the incoming proactive signal.

Enum: OutreachStatus

Values:
- OUTREACH_CREATED
- SUPPRESSED
- ESCALATION_REQUIRED
- NO_ACTION

Purpose:
Final workflow execution status returned in ProactiveOutput.

---

### File: schemas/signal.py

**Purpose**

Input contract for signals entering the proactive agent workflow.

**Schemas/Models**

Schema: Signal

Fields:
- signal_id: str (unique string identifier)
- customer_id: int (>0, must be positive, matches DB bigint)
- signal_type: SignalType (enum from enums.py)
- signal_source: SignalSource (default: SignalSource.CRM)
- signal_context: Dict[str, Any] (flexible metadata, examples: churn_score, ticket_id, days_inactive)
- detected_at: datetime (UTC timestamp, default: now)

Purpose:
Business entry contract for the Proactive Agent. Represents a validated proactive trigger entering the LangGraph orchestration workflow. Immutable (frozen=True).

**Relationships**

Used By:
- validate_signal_node
- customer_context_node
- suppression_gate_node
- signal_analysis_node
- message_generation_node
- escalation_handoff_node

---

### File: schemas/signal_assessment.py

**Purpose**

Output schema from signal_analysis_node converting raw Signal into business-level assessment.

**Schemas/Models**

Schema: SignalAssessment

Fields:
- signal_type: SignalType (enum, copy from incoming Signal)
- severity: RiskLevel (enum, business severity assigned to the signal)
- detected_reason: str (human-readable explanation of why signal was triggered)
- requires_immediate_attention: bool (default: False, indicates immediate action should be considered)

Purpose:
Intermediate contract produced by signal_analysis_node. Converts raw signal into interpreted business assessment consumed by downstream risk scoring and decision nodes. Immutable (frozen=True).

**Relationships**

Consumes:
- Signal

Produces:
- RiskAssessment (downstream)

Used By:
- risk_scoring_node
- message_generation_node
- escalation_handoff_node
- response_node

---

### File: schemas/risk_assessment.py

**Purpose**

Output schema from risk_scoring_node representing final business risk evaluation.

**Schemas/Models**

Schema: RiskAssessment

Fields:
- risk_level: RiskLevel (enum, final business risk level)
- risk_score: Decimal (0-100, normalized risk score with 2 decimal places)
- risk_reasons: list[str] (default: [], human-readable reasons contributing to risk score)
- escalation_candidate: bool (default: False, whether customer should be escalated)
- computed_at: datetime (UTC timestamp, default: now, matches DB timestamp with time zone)

Purpose:
Final business risk assessment produced by risk_scoring_node. Used by outreach_decision_node to determine next workflow path. Immutable (frozen=True).

**Relationships**

Consumes:
- SignalAssessment
- CustomerProfile

Produces:
- OutreachDecision (downstream)

Used By:
- outreach_decision_node
- message_generation_node
- escalation_handoff_node
- response_node

---

### File: schemas/outreach_decision.py

**Purpose**

Output schema from outreach_decision_node representing final workflow orchestration decision.

**Schemas/Models**

Schema: OutreachDecision

Fields:
- action: OutreachAction (enum, NO_ACTION/OUTREACH/ESCALATE)
- reason: str (business explanation for selected action)
- review_required: bool (default: False, whether human review is recommended)
- escalation_reason: str (optional, reason escalation was selected)
- decided_at: datetime (UTC timestamp, default: now)

Purpose:
Final orchestration decision that determines next graph path (message generation, escalation, or response). Immutable (frozen=True).

**Relationships**

Consumes:
- RiskAssessment

Produces:
- OutreachMessage (if action=OUTREACH)
- EscalationHandoff (if action=ESCALATE)

Used By:
- decision_router
- message_generation_node
- escalation_handoff_node
- response_node

---

### File: schemas/outreach_message.py

**Purpose**

Output schema from message_generation_node containing customer-facing LLM-generated message.

**Schemas/Models**

Schema: OutreachMessage

Fields:
- subject: str (subject line of outreach message)
- body: str (generated outreach message content)
- channel: str (default: "email", delivery channel)
- generated_by: str (model or system responsible for generation, e.g., "llama3-70b-8192")
- generated_at: datetime (UTC timestamp, default: now, matches DB timestamp with time zone)

Purpose:
Final customer-facing outreach message generated by LLM layer. Present only when workflow status=OUTREACH_CREATED. Immutable (frozen=True).

**Relationships**

Produces:
- ProactiveOutput (included in final output)

Used By:
- response_node

---

### File: schemas/escalation_handoff.py

**Purpose**

Normalized contract for transferring critical proactive cases to Escalation Agent (Layer 3).

**Schemas/Models**

Schema: EscalationHandoff

Fields:
- ticket_id: str (system-generated escalation ticket ID, format: ESC-{workflow_id})
- customer_id: int (matches DB bigint type)
- customer_email: EmailStr (validated email address)
- source_agent: str (default: "proactive_agent", agent creating escalation)
- initial_intent: str (intent assigned to escalation)
- initial_sentiment: str (customer sentiment that triggered escalation)
- initial_urgency: str (urgency assigned by proactive risk evaluation)
- supervisor_confidence: float (default: 1.0, 0-1 range, confidence associated with routing)
- message_raw: str (original escalation message)
- message_english: str (English version of escalation message)
- created_at: datetime (UTC timestamp, default: now)

Purpose:
Escalation handoff contract for downstream Escalation Agent workflow. Packages full customer context for human supervisor review. Immutable (frozen=True).

**Relationships**

Produces:
- ProactiveOutput (included in final output when escalated)

Used By:
- escalation_handoff_node
- response_node

---

### File: schemas/proactive_output.py

**Purpose**

Public output contract of the Proactive Agent (Layer 2) returned to CRM Agent and orchestration layers.

**Schemas/Models**

Schema: ProactiveOutput

Fields:
- workflow_id: str (unique workflow identifier matching DB varchar type)
- agent_id: str (default: "proactive_agent", agent producing this output)
- status: OutreachStatus (enum, final workflow status)
- customer_id: int (customer identifier matching DB bigint type)
- signal_assessment: Optional[SignalAssessment] (produced by signal_analysis_node, None if suppressed early)
- risk_assessment: Optional[RiskAssessment] (final business risk assessment, None if suppressed early)
- decision: Optional[OutreachDecision] (final orchestration decision, None if suppressed early)
- outreach_message: Optional[OutreachMessage] (generated outreach message, present only when status=OUTREACH_CREATED)
- escalation_handoff: Optional[EscalationHandoff] (escalation package, present only when status=ESCALATION_REQUIRED)

Purpose:
Canonical public output contract of Proactive Agent. Consumed by CRM Agent, integration tests, end-to-end workflows, and future orchestration layers. Immutable (frozen=True).

**Relationships**

Produces:
- CRMResolvedEvent (via ProactiveAdapter)

Used By:
- response_node
- Integration tests
- CRM Agent Layer 1

---

### File: schemas/proactive_state.py

**Purpose**

LangGraph workflow state object shared across all orchestration nodes.

**Schemas/Models**

Schema: ProactiveState

Fields:
- workflow_id: str (unique workflow identifier)
- signal_id: str (unique signal identifier)
- status: str (current workflow status)
- signal: Signal (incoming validated signal)
- customer_profile: Optional[CustomerProfile] (loaded from CRM database)
- signal_assessment: Optional[SignalAssessment] (produced by signal_analysis_node)
- risk_assessment: Optional[RiskAssessment] (produced by risk_scoring_node)
- decision: Optional[OutreachDecision] (produced by outreach_decision_node)
- outreach_message: Optional[OutreachMessage] (produced by message_generation_node)
- escalation_handoff: Optional[EscalationHandoff] (produced by escalation_handoff_node)
- output: Optional[ProactiveOutput] (produced by response_node)
- suppressed: bool (flag indicating early suppression)
- suppression_reason: Optional[str] (reason for suppression)
- current_node: Optional[str] (current executing node name)
- workflow_logs: List[Dict[str, Any]] (audit trail of node executions)
- errors: List[str] (accumulated error messages)

Purpose:
Mutable orchestration memory shared across all graph nodes. Tracks workflow progression and node outputs. TypedDict-based for type safety.

---

### File: adapters/proactive_adapter.py

**Purpose**

Adapter translating internal ProactiveOutput into canonical CRMResolvedEvent contract.

**Classes**

Class: ProactiveAdapter
Type: Adapter

Methods:
- to_crm_event(output: ProactiveOutput) -> CRMResolvedEvent

Purpose:
Bridges Proactive Agent output to CRM event schema. Maps OutreachStatus values to event types, statuses, and resolution metadata. Handles mapping of all four status paths (SUPPRESSED, ESCALATION_REQUIRED, OUTREACH_CREATED, NO_ACTION).

**Relationships**

Consumes:
- ProactiveOutput

Produces:
- CRMResolvedEvent

---

### File: config/constants.py

**Purpose**

Empty configuration constants file (reserved for future use).

---

### File: main.py

**Purpose**

Empty main entry point (reserved for FastAPI/CLI implementation).

---

### File: repositories/proactive_outreach_repository.py

**Purpose**

Repository for suppression registry and outreach persistence operations.

**Classes**

Class: ProactiveOutreachRepository
Type: Repository

Methods:
- already_contacted(customer_id: int, signal_type: str) -> Optional[ProactiveOutreachRecord]
- record_outreach(record: ProactiveOutreachRecord) -> ProactiveOutreachRecord
- record_suppression(record: ProactiveOutreachRecord) -> ProactiveOutreachRecord
- cleanup_expired_records(retention_days: int = 90) -> int
- get_active_suppressions(customer_id: int) -> List[ProactiveOutreachRecord]

Purpose:
Handles suppression lookups, outreach persistence, suppression persistence, and cleanup operations. Transaction commit is managed by caller.

**Database**

Database:
- PostgreSQL

Tables Referenced:
- proactive_outreach_registry

**Relationships**

Consumes:
- ProactiveOutreachRecord

Used By:
- SuppressionService
- suppression_gate_node
- message_generation_node
- escalation_handoff_node

---

### File: repositories/proactive_event_repository.py

**Purpose**

Repository for proactive workflow audit event persistence and retrieval.

**Classes**

Class: ProactiveEventRepository
Type: Repository

Methods:
- save_event(event: ProactiveEventRecord) -> ProactiveEventRecord
- get_by_workflow(workflow_id: str) -> Optional[ProactiveEventRecord]
- get_customer_history(customer_id: int) -> list[ProactiveEventRecord]
- get_signal_history(signal_type: str) -> list[ProactiveEventRecord]

Purpose:
Handles persistence and lookup of workflow audit events. Supports querying by workflow ID, customer ID, and signal type.

**Database**

Database:
- PostgreSQL

Tables Referenced:
- proactive_events

**Relationships**

Consumes:
- ProactiveEventRecord

---

### File: repositories/customer_profile_repository.py

**Purpose**

Empty customer profile repository (external dependency from CRM Agent layer).

---

### File: repositories/transcript_repository.py

**Purpose**

Empty transcript repository (reserved for future transcript enrichment).

---

### File: services/signal_detection_service.py

**Purpose**

Converts incoming signals into business-level assessments based on signal type.

**Classes**

Class: SignalDetectionService
Type: Service

Methods:
- analyze(signal: Signal) -> SignalAssessment

Purpose:
Maps incoming signal types to predefined severity levels and detected reasons. Produces SignalAssessment for downstream risk scoring.

**Relationships**

Consumes:
- Signal

Produces:
- SignalAssessment

Used By:
- signal_analysis_node

---

### File: services/risk_engine.py

**Purpose**

Computes final business risk assessment from signal intelligence and customer profile.

**Classes**

Class: RiskEngine
Type: Service

Methods:
- assess(signal_assessment: SignalAssessment, customer_profile: CustomerProfile) -> RiskAssessment

Constants:
- SEVERITY_SCORES (dict mapping RiskLevel to numeric scores: LOW=10, MEDIUM=30, HIGH=60, CRITICAL=90)
- CHURN_SCORES (dict mapping churn_level to scores: LOW=10, MEDIUM=30, HIGH=60, CRITICAL=90)
- TIER_SCORES (dict: standard=0, premium=10, enterprise=20)

Purpose:
Risk scoring engine combining signal severity, customer churn level, tier, and negative history. Outputs RiskAssessment with normalized 0-100 risk score and escalation flag.

**Relationships**

Consumes:
- SignalAssessment
- CustomerProfile

Produces:
- RiskAssessment

Used By:
- risk_scoring_node

---

### File: services/outreach_decision_service.py

**Purpose**

Determines final proactive workflow action from business risk assessment.

**Classes**

Class: OutreachDecisionService
Type: Service

Methods:
- decide(risk_assessment: RiskAssessment) -> OutreachDecision

Constants:
- OUTREACH_CONFIDENCE = 0.85
- ESCALATION_CONFIDENCE = 1.0
- NO_ACTION_CONFIDENCE = 1.0

Purpose:
Decision logic mapping risk levels to actions. Escalates if escalation_candidate=True or risk=CRITICAL/HIGH. Otherwise routes to OUTREACH or NO_ACTION.

**Relationships**

Consumes:
- RiskAssessment

Produces:
- OutreachDecision

Used By:
- outreach_decision_node

---

### File: services/message_generation_service.py

**Purpose**

Generates customer-facing outreach messages using LLM with dynamic prompt architecture.

**Classes**

Class: MessageGenerationService
Type: Service

Methods:
- generate(customer_profile: CustomerProfile, risk_assessment: RiskAssessment, signal_assessment: SignalAssessment) -> OutreachMessage
- _get_signal_prompt(signal_type: SignalType) -> str (private)
- _build_customer_context(customer_profile: CustomerProfile, risk_assessment: RiskAssessment, signal_assessment: SignalAssessment) -> str (private)
- _invoke_llm(system_prompt: str, human_prompt: str) -> OutreachMessage (private, with retry logic)

Constants:
- MODEL_NAME = "llama-3.3-70b-versatile"
- TEMPERATURE = 0.3
- LANGUAGE_MAP (dict mapping language codes to English names)

Purpose:
LLM-powered message generation. Uses Groq API with structured output. Maps signals to intent-specific prompts. Supports multi-language output with fallback template.

**Dependencies**

Dependencies:
- ChatGroq (Groq LLM client)
- tenacity (retry logic)
- langchain_groq

**Relationships**

Consumes:
- CustomerProfile
- RiskAssessment
- SignalAssessment
- Signal prompts (base_prompt.py, signal-specific prompts)

Produces:
- OutreachMessage

Used By:
- message_generation_node

---

### File: services/escalation_service.py

**Purpose**

Creates escalation handoff contracts for downstream Escalation Agent workflows (Layer 3).

**Classes**

Class: EscalationService
Type: Service

Methods:
- handoff(workflow_id: str, customer_profile: CustomerProfile, signal_assessment: SignalAssessment, risk_assessment: RiskAssessment) -> EscalationHandoff

Constants:
- URGENCY_MAPPING (dict: RiskLevel -> urgency_string: LOW=low, MEDIUM=medium, HIGH=high, CRITICAL=urgent)

Purpose:
Packages customer context and risk assessment into EscalationHandoff contract. Creates deterministic ticket ID from workflow_id. Generates escalation message with full context.

**Relationships**

Consumes:
- CustomerProfile
- SignalAssessment
- RiskAssessment

Produces:
- EscalationHandoff

Used By:
- escalation_handoff_node

---

### File: services/suppression_service.py

**Purpose**

Business rules for suppression registry and outreach management.

**Classes**

Class: SuppressionService
Type: Service

Methods:
- should_suppress(customer_id: int, signal_type: SignalType) -> Tuple[bool, Optional[str]]
- calculate_expiry(signal_type: SignalType) -> datetime
- create_outreach_record(workflow_id: str, signal_id: str, customer_id: int, signal_type: SignalType, decision: str) -> ProactiveOutreachRecord
- create_suppression_record(workflow_id: str, signal_id: str, customer_id: int, signal_type: SignalType) -> ProactiveOutreachRecord

Constants:
- SUPPRESSION_WINDOWS (dict: SignalType -> days; INACTIVE_CUSTOMER=30, HIGH_CHURN_RISK=14, RECENT_NEGATIVE_EXPERIENCE=14, VIP_RETENTION_RISK=7)

Purpose:
Suppression and cooldown window logic. Prevents duplicate outreach to customers within configured suppression windows per signal type. Calculates expiry dates and creates suppression records.

**Dependencies**

Dependencies:
- ProactiveOutreachRepository

**Relationships**

Consumes:
- ProactiveOutreachRepository

Produces:
- ProactiveOutreachRecord (suppression/outreach records)

Used By:
- suppression_gate_node
- message_generation_node
- escalation_handoff_node

---

### File: services/proactive_orchestrator.py

**Purpose**

Empty main orchestrator service (reserved for future orchestration logic).

---

### File: utils/logger.py

**Purpose**

Centralized logging configuration for the proactive agent module.

**Functions**

Function: logger

Returns:
logging.Logger

Purpose:
Configured logger instance named "proactive_agent" with standard format including timestamp, level, module, and message.

---

### File: utils/exceptions.py

**Purpose**

Empty exceptions module (reserved for custom exception definitions).

---

### File: utils/id_generator.py

**Purpose**

Empty ID generation utilities (reserved for UUID/ID generation helpers).

---

### File: utils/datetime_utils.py

**Purpose**

Empty datetime utilities (reserved for timezone and date manipulation helpers).

---

### File: utils/score_utils.py

**Purpose**

Empty score utilities (reserved for scoring/normalization helpers).

---

### File: prompts/base_prompt.py

**Purpose**

System-level prompt defining core behavior for LLM message generation.

**Constants**

```
BASE_SYSTEM_PROMPT = """
[System prompt text - defines tone, constraints, personalization, risk-level guidance, anti-hallucination policy, language rules, and structured output requirements]
"""
```

Purpose:
Foundation system prompt for all message generation. Defines tone (empathetic, professional), constraints (no compensation, no false promises), personalization rules, risk-level guidance (LOW→friendly, MEDIUM→assist, HIGH→concern, CRITICAL→care), anti-hallucination policy, and structured output format.

Used By:
- MessageGenerationService

---

### File: prompts/high_churn_prompt.py

**Purpose**

Intent-specific prompt for HIGH_CHURN_RISK signal.

**Constants**

```
CHURN_PROMPT = """
[Specific prompt for high churn risk detection - goals: uncover root cause, demonstrate proactive care, offer strategic assistance, encourage reply]
"""
```

Purpose:
Appended to BASE_SYSTEM_PROMPT for churn-specific message generation. Focus on understanding customer concerns, offering support without defensiveness, avoiding internal terminology, subject line under 8 words.

Used By:
- MessageGenerationService

---

### File: prompts/inactive_customer_prompt.py

**Purpose**

Intent-specific prompt for INACTIVE_CUSTOMER signal.

**Constants**

```
INACTIVE_CUSTOMER_PROMPT = """
[Specific prompt for inactive customer re-engagement - goals: gentle re-engagement, offer unblocking support, open-ended check-in, encourage reply]
"""
```

Purpose:
Appended to BASE_SYSTEM_PROMPT for inactive customer messages. Focus on gentle re-engagement without guilt-trip language, assume they might be busy, not necessarily churning. Avoid sales language.

Used By:
- MessageGenerationService

---

### File: prompts/negative_experience_prompt.py

**Purpose**

Intent-specific prompt for RECENT_NEGATIVE_EXPERIENCE signal.

**Constants**

```
NEGATIVE_EXPERIENCE_PROMPT = """
[Specific prompt for relationship repair - goals: acknowledge and validate, show empathy, rebuild trust, encourage reply]
"""
```

Purpose:
Appended to BASE_SYSTEM_PROMPT for negative experience recovery. Focus on listening, acknowledging friction, relationship repair, avoiding defensiveness or excuses. Subject line under 8 words with empathetic tone.

Used By:
- MessageGenerationService

---

### File: prompts/vip_retention_prompt.py

**Purpose**

Intent-specific prompt for VIP_RETENTION_RISK signal.

**Constants**

```
VIP_RETENTION_PROMPT = """
[Specific prompt for strategic customer retention - goals: acknowledge partnership, reinforce strategic alignment, provide concierge-level care, encourage reply]
"""
```

Purpose:
Appended to BASE_SYSTEM_PROMPT for VIP/enterprise customers. Focus on business outcomes, strategic partnership, listening before solving, maintaining executive presence without sounding panicked. Subject line under 8 words, partnership-focused tone.

Used By:
- MessageGenerationService

---

### File: nodes/validate_signal_node.py

**Purpose**

Gatekeeper node ensuring incoming signal is structurally valid and contains required business context.

**Functions**

Function: validate_signal_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object)

Returns:
Dict[str, Any] (updated state with validation logs or raises ValueError)

Purpose:
Fails fast on malformed signals, missing customer IDs, unsupported signal types, or missing required signal_context fields. Validates both structure and business logic requirements.

**Relationships**

Consumes:
- ProactiveState with Signal

Produces:
- Updated ProactiveState with workflow logs

Entry Point:
- START (graph entry)

---

### File: nodes/customer_context_node.py

**Purpose**

Loads customer intelligence from CRM database and enriches workflow state.

**Functions**

Function: customer_context_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object)

Returns:
Dict[str, Any] (updated state with CustomerProfile or raises ValueError)

Purpose:
Queries CustomerProfileRepository to fetch customer profile. Maps flat database columns into nested Pydantic schemas (SentimentProfile, ChurnMetrics). Handles missing profiles with explicit error.

**Dependencies**

Dependencies:
- CustomerProfileRepository
- SessionLocal (database session)

**Relationships**

Consumes:
- ProactiveState with Signal

Produces:
- CustomerProfile

---

### File: nodes/suppression_gate_node.py

**Purpose**

Checks whether a customer is currently under an active suppression window.

**Functions**

Function: suppression_gate_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object)

Returns:
Dict[str, Any] (updated state with suppressed flag and reason)

Purpose:
Routes suppressed workflows directly to response_node. Checks ProactiveOutreachRepository for active records that haven't expired.

**Dependencies**

Dependencies:
- ProactiveOutreachRepository
- SuppressionService

**Relationships**

Consumes:
- ProactiveState with Signal

Produces:
- suppressed flag (bool)
- suppression_reason (optional str)

Router:
- suppression_router (routes to signal_analysis_node or response_node)

---

### File: nodes/signal_analysis_node.py

**Purpose**

Converts incoming signals into business-level assessments.

**Functions**

Function: signal_analysis_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object)

Returns:
Dict[str, Any] (updated state with SignalAssessment or raises Exception)

Purpose:
Calls SignalDetectionService.analyze() to map signal types to severity levels and reasons. Produces SignalAssessment for downstream risk scoring.

**Dependencies**

Dependencies:
- SignalDetectionService

**Relationships**

Consumes:
- Signal

Produces:
- SignalAssessment

---

### File: nodes/risk_scoring_node.py

**Purpose**

Computes final business risk assessment from signal intelligence and customer profile.

**Functions**

Function: risk_scoring_node(state: ProactiveState) -> dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object with signal_assessment and customer_profile)

Returns:
dict[str, Any] (updated state with RiskAssessment or raises Exception)

Purpose:
Calls RiskEngine.assess() combining signal severity, customer churn level, tier, and negative history. Produces RiskAssessment with normalized 0-100 score.

**Dependencies**

Dependencies:
- RiskEngine

**Relationships**

Consumes:
- SignalAssessment
- CustomerProfile

Produces:
- RiskAssessment

---

### File: nodes/outreach_decision_node.py

**Purpose**

Evaluates computed risk and determines final workflow action.

**Functions**

Function: outreach_decision_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state object with risk_assessment)

Returns:
Dict[str, Any] (updated state with OutreachDecision or raises Exception)

Purpose:
Calls OutreachDecisionService.decide() to map risk assessment to action (OUTREACH, ESCALATE, or NO_ACTION).

**Dependencies**

Dependencies:
- OutreachDecisionService

**Relationships**

Consumes:
- RiskAssessment

Produces:
- OutreachDecision

Router:
- decision_router (routes to message_generation_node, escalation_handoff_node, or response_node)

---

### File: nodes/message_generation_node.py

**Purpose**

Generates personalized outreach message using LLM layer and registers in suppression registry.

**Functions**

Function: message_generation_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state with customer_profile, risk_assessment, signal_assessment, decision)

Returns:
Dict[str, Any] (updated state with OutreachMessage or raises Exception)

Purpose:
Calls MessageGenerationService.generate() for LLM message creation. Persists outreach record to ProactiveOutreachRepository for suppression tracking. Handles database transactions with rollback on failure.

**Dependencies**

Dependencies:
- MessageGenerationService
- ProactiveOutreachRepository
- SuppressionService
- SessionLocal

**Relationships**

Consumes:
- CustomerProfile
- RiskAssessment
- SignalAssessment
- Signal

Produces:
- OutreachMessage

Used By:
- decision_router (routed from outreach_decision_node)

---

### File: nodes/escalation_handoff_node.py

**Purpose**

Packages customer context for human supervisor review (Layer 3) and registers escalation in suppression registry.

**Functions**

Function: escalation_handoff_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (workflow state with customer_profile, signal_assessment, risk_assessment, decision)

Returns:
Dict[str, Any] (updated state with EscalationHandoff or raises Exception)

Purpose:
Calls EscalationService.handoff() to package escalation ticket. Persists escalation record to ProactiveOutreachRepository for suppression/audit tracking. Handles database transactions with rollback.

**Dependencies**

Dependencies:
- EscalationService
- ProactiveOutreachRepository
- SuppressionService
- SessionLocal

**Relationships**

Consumes:
- CustomerProfile
- SignalAssessment
- RiskAssessment
- Signal

Produces:
- EscalationHandoff

Used By:
- decision_router (routed from outreach_decision_node)

---

### File: nodes/response_node.py

**Purpose**

Final API boundary node packaging internal LangGraph state into public ProactiveOutput contract.

**Functions**

Function: response_node(state: ProactiveState) -> Dict[str, Any]

Parameters:
- state: ProactiveState (final workflow state)

Returns:
Dict[str, Any] (final state with ProactiveOutput or raises ValueError)

Purpose:
Extracts path-dependent context from state. Determines final OutreachStatus. Constructs and returns ProactiveOutput contract matching DB constraints. Final node before workflow END.

**Relationships**

Consumes:
- ProactiveState (all fields)

Produces:
- ProactiveOutput

Exit Point:
- END (graph exit)

---

### File: graph/proactive_graph.py

**Purpose**

LangGraph state machine assembling the decoupled proactive agent workflow.

**Classes**

Class: (Graph building function)

Functions:
- build_proactive_graph() -> CompiledGraph

Purpose:
Constructs the LangGraph state machine. Returns compiled graph with memory checkpointer.

**State Object**

State Object:
- ProactiveState

**Nodes**

Nodes:
- validate_signal_node
- customer_context_node
- suppression_gate_node
- signal_analysis_node
- risk_scoring_node
- outreach_decision_node
- message_generation_node
- escalation_handoff_node
- response_node

**Routers**

Routers:
- suppression_router (suppression_gate_node → signal_analysis_node or response_node)
- decision_router (outreach_decision_node → message_generation_node, escalation_handoff_node, or response_node)

**Entry Point**

Entry Point:
- validate_signal_node (from START)

**Exit Point**

Exit Point:
- response_node (to END)

**Edge Flow**

Edge Flow:
1. START → validate_signal_node
2. validate_signal_node → customer_context_node
3. customer_context_node → suppression_gate_node
4. suppression_gate_node → (suppression_router) → signal_analysis_node OR response_node
5. signal_analysis_node → risk_scoring_node
6. risk_scoring_node → outreach_decision_node
7. outreach_decision_node → (decision_router) → message_generation_node OR escalation_handoff_node OR response_node
8. message_generation_node → response_node
9. escalation_handoff_node → response_node
10. response_node → END

**Relationships**

Global Instance:
- proactive_graph (compiled graph accessible for invocation)

---

### File: graph/routers.py

**Purpose**

LangGraph conditional edge routers for path routing based on node outputs.

**Functions**

Function: suppression_router(state: ProactiveState) -> str

Parameters:
- state: ProactiveState (with suppressed flag)

Returns:
str (routing target: "signal_analysis_node" or "response_node")

Purpose:
Routes suppressed workflows directly to response_node. Non-suppressed workflows proceed to signal_analysis_node.

Function: decision_router(state: ProactiveState) -> str

Parameters:
- state: ProactiveState (with decision object)

Returns:
str (routing target: "message_generation_node", "escalation_handoff_node", or "response_node")

Purpose:
Routes based on OutreachDecision.action: OUTREACH→message_generation_node, ESCALATE→escalation_handoff_node, NO_ACTION→response_node.

---

### File: graph/state_factory.py

**Purpose**

Factory for creating initial LangGraph workflow state from incoming Signal.

**Classes**

Class: ProactiveStateFactory
Type: Factory

Methods:
- create(signal: Signal) -> ProactiveState (static method)

Purpose:
Initializes ProactiveState with unique workflow_id (format: PRO-{uuid}), incoming signal, and empty nullable fields. Every proactive workflow starts here.

**Relationships**

Consumes:
- Signal

Produces:
- ProactiveState (initial state)

Used By:
- Graph invocation (external integration)

---

### File: integration/crm_integration.py

**Purpose**

Empty CRM integration module (reserved for future CRM system integration).

---

### File: integration/escalation_integration.py

**Purpose**

Empty escalation integration module (reserved for future Escalation Agent (Layer 3) integration).

---

---

## Section 3: Folder Summary

### Folder Purpose

The Layer 2 Proactive Agent is a LangGraph-based workflow orchestrator that detects and responds to customer signals (churn risk, inactivity, negative experiences, VIP retention) with intelligent, LLM-powered outreach or escalation. It bridges CRM customer intelligence with risk assessment and decision engines to enable proactive customer retention at scale.

### Files Included

**Core Files:**
- config/constants.py
- config/settings.py
- config/__init__.py
- main.py
- README.md
- proactive_agent_playground.ipynb

**Database:**
- database/__init__.py
- database/base.py
- database/session.py
- database/model/__init__.py
- database/model/proactive_event_record.py
- database/model/proactive_outreach_record.py

**Schemas:**
- schemas/__init__.py
- schemas/enums.py
- schemas/signal.py
- schemas/signal_assessment.py
- schemas/risk_assessment.py
- schemas/outreach_decision.py
- schemas/outreach_message.py
- schemas/escalation_handoff.py
- schemas/proactive_state.py
- schemas/proactive_output.py

**Services:**
- services/__init__.py
- services/signal_detection_service.py
- services/risk_engine.py
- services/outreach_decision_service.py
- services/message_generation_service.py
- services/escalation_service.py
- services/suppression_service.py
- services/proactive_orchestrator.py

**Repositories:**
- repositories/__init__.py
- repositories/customer_profile_repository.py
- repositories/proactive_outreach_repository.py
- repositories/proactive_event_repository.py
- repositories/transcript_repository.py

**Graph Nodes:**
- nodes/__init__.py
- nodes/validate_signal_node.py
- nodes/customer_context_node.py
- nodes/suppression_gate_node.py
- nodes/signal_analysis_node.py
- nodes/risk_scoring_node.py
- nodes/outreach_decision_node.py
- nodes/message_generation_node.py
- nodes/escalation_handoff_node.py
- nodes/response_node.py

**Graph:**
- graph/__init__.py
- graph/proactive_graph.py
- graph/routers.py
- graph/state_factory.py

**Prompts:**
- prompts/__init__.py
- prompts/base_prompt.py
- prompts/high_churn_prompt.py
- prompts/inactive_customer_prompt.py
- prompts/negative_experience_prompt.py
- prompts/vip_retention_prompt.py

**Adapters:**
- adapters/__init__.py
- adapters/proactive_adapter.py

**Integration:**
- integration/__init__.py
- integration/crm_integration.py
- integration/escalation_integration.py

**Utilities:**
- utils/__init__.py
- utils/logger.py
- utils/exceptions.py
- utils/id_generator.py
- utils/datetime_utils.py
- utils/score_utils.py

**Evaluation:**
- evaluation/__init__.py
- evaluation/eval_runner.py
- evaluation/metrics.py
- evaluation/datasets/churn_cases.json
- evaluation/datasets/proactive_negative_cases.json
- evaluation/datasets/proactive_positive_cases.json
- evaluation/datasets/vip_cases.json

**Tests:**
- tests/conftest.py
- tests/fixtures/churn_fixtures.py
- tests/fixtures/customer_profiles.py
- tests/fixtures/signal_fixtures.py
- tests/fixtures/transcript_fixtures.py
- tests/unit/test_adapter.py
- tests/unit/test_customer_context_node.py
- tests/unit/test_escalation_handoff_node.py
- tests/unit/test_message_generation_node.py
- tests/unit/test_outreach_decision_node.py
- tests/unit/test_responce_node.py
- tests/unit/test_risk_engine.py
- tests/unit/test_risk_scoring_node.py
- tests/unit/test_signal_analysis_node.py
- tests/unit/test_suppression_gate_node.py
- tests/unit/test_suppression_service.py
- tests/unit/test_validate_signal_node.py
- tests/integration/test_crm_event_creation.py
- tests/integration/test_escalation_contract.py
- tests/integration/test_full_escalation_flow.py
- tests/integration/test_full_outreach_flow.py
- tests/integration/test_outreach_registry.py
- tests/e2e/test_end_to_end_proactive_agent.py

### Main Components

**Repositories:**
- ProactiveOutreachRepository (suppression registry management)
- ProactiveEventRepository (workflow audit events)
- CustomerProfileRepository (external CRM dependency)
- TranscriptRepository (reserved for future use)

**Services:**
- SignalDetectionService (signal→assessment mapping)
- RiskEngine (risk scoring)
- OutreachDecisionService (decision logic)
- MessageGenerationService (LLM-powered message generation)
- EscalationService (escalation handoff)
- SuppressionService (suppression/cooldown management)

**Schemas:**
- Signal (input contract)
- SignalAssessment (signal analysis output)
- RiskAssessment (risk scoring output)
- OutreachDecision (decision output)
- OutreachMessage (LLM message output)
- EscalationHandoff (escalation contract)
- ProactiveOutput (final output contract)
- ProactiveState (workflow state)

**Enums:**
- SignalType (INACTIVE_CUSTOMER, HIGH_CHURN_RISK, RECENT_NEGATIVE_EXPERIENCE, VIP_RETENTION_RISK)
- RiskLevel (LOW, MEDIUM, HIGH, CRITICAL)
- OutreachAction (NO_ACTION, OUTREACH, ESCALATE)
- SignalSource (CRM, STRIPE, SHOPIFY, STATUS_PAGE, SYSTEM)
- OutreachStatus (OUTREACH_CREATED, SUPPRESSED, ESCALATION_REQUIRED, NO_ACTION)

**Graphs:**
- proactive_graph (LangGraph state machine with 9 nodes and 2 routers)

**Models:**
- ProactiveEventRecord (PostgreSQL audit table)
- ProactiveOutreachRecord (PostgreSQL suppression registry)

**Utilities:**
- logger (standardized logging)
- exceptions (reserved for custom exceptions)
- id_generator (reserved for ID generation)
- datetime_utils (reserved for datetime manipulation)
- score_utils (reserved for scoring utilities)

### Input / Output

**Input:**
- Signal (signal_id, customer_id, signal_type, signal_context, detected_at)

**Output:**
- ProactiveOutput (workflow_id, status, customer_id, signal_assessment, risk_assessment, decision, outreach_message, escalation_handoff)

**Intermediate Outputs (by node):**
- signal_analysis_node → SignalAssessment
- risk_scoring_node → RiskAssessment
- outreach_decision_node → OutreachDecision
- message_generation_node → OutreachMessage
- escalation_handoff_node → EscalationHandoff

---

## Workflow Path Summary

**Happy Path (Outreach):**
Signal → Validate → Customer Context → Suppression Check (not suppressed) → Signal Analysis → Risk Scoring (risk=HIGH/MEDIUM) → Decision (action=OUTREACH) → Message Generation → Response → Output

**Escalation Path:**
Signal → Validate → Customer Context → Suppression Check (not suppressed) → Signal Analysis → Risk Scoring (risk=CRITICAL or escalation_candidate=True) → Decision (action=ESCALATE) → Escalation Handoff → Response → Output

**No-Action Path:**
Signal → Validate → Customer Context → Suppression Check (not suppressed) → Signal Analysis → Risk Scoring (risk=LOW) → Decision (action=NO_ACTION) → Response → Output

**Suppression Path:**
Signal → Validate → Customer Context → Suppression Check (suppressed) → Response → Output


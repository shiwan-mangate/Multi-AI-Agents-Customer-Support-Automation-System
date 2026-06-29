# Codebase Inventory: `layer_2_escalation_agent`

---

# Section 1: Folder Structure

```text
layer_2_escalation_agent/
│
├── config/
│   ├── __init__.py
│   └── constants.py
│
├── db/
│   ├── __init__.py
│   └── session.py
│
├── factories/
│   ├── __init__.py
│   └── state_factory.py
│
├── graph/
│   ├── __init__.py
│   ├── escalation_graph.py
│   └── routers.py
│
├── mapper/
│   └── escalation_final_responce.py
│
├── nodes/
│   ├── __init__.py
│   ├── brief_generation_node.py
│   ├── case_persistence_node.py
│   ├── conversation_context_node.py
│   ├── customer_context_node.py
│   ├── holding_response_node.py
│   ├── human_review_node.py
│   ├── notification_dispatch_node.py
│   ├── response_node.py
│   ├── risk_scoring_node.py
│   ├── routing_decision_node.py
│   ├── sla_tracking_node.py
│   ├── trigger_assessment_node.py
│   └── validate_contract_node.py
│
├── prompts/
│   ├── __init__.py
│   └── escalation_brief_prompt.py
│
├── repositories/
│   ├── __init__.py
│   ├── agent_action_repository.py
│   ├── audit_repository.py
│   ├── conversation_repository.py
│   ├── customer_repository.py
│   ├── escalation_repository.py
│   ├── notification_outbox_repository.py
│   └── ticket_repository.py
│
├── schemas/
│   ├── __init__.py
│   ├── audit_record.py
│   ├── conversation_context.py
│   ├── customer_context.py
│   ├── escalation_output.py
│   ├── escalation_response.py
│   ├── escalation_state.py
│   ├── human_brief.py
│   ├── human_decision.py
│   ├── notification_job.py
│   ├── risk_assessment.py
│   ├── routing_decision.py
│   └── trigger_assessment.py
│
├── services/
│   ├── __init__.py
│   ├── brief_generation_service.py
│   ├── escalation_agent.py
│   ├── holding_response_service.py
│   ├── notification_service.py
│   ├── risk_engine.py
│   ├── routing_service.py
│   └── trigger_engine.py
│
├── tests/
│   ├── test_brief_generation.py
│   ├── test_duplicate_guard.py
│   ├── test_graph_flow.py
│   ├── test_risk_engine.py
│   └── test_trigger_engine.py
│
├── utils/
│   ├── __init__.py
│   ├── ids.py
│   ├── logging_utils.py
│   └── time_utils.py
│
├── .gitignore
├── __init__.py
├── dependencies.py
├── main.py
├── test_escalation_agent.ipynb
└── test_escalation_agent_suite.py
```

---

# Section 2: File Analysis

## Root Directory

---

### File: `__init__.py`

**Purpose**
Empty initialization file for Python module packaging.

**Classes:** None
**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

---

### File: `dependencies.py`

**Purpose**
Shared third-party API clients and dependency providers.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: get_llm_client()

Parameters:
- None

Returns:
- ChatGroq

Purpose:
Instantiates a LangChain ChatGroq model client using the GROQ_API_KEY environment variable.
```

**Constants:** None

**Relationships**
- Produces: `ChatGroq` client
- Used By: `nodes/brief_generation_node.py`

---

### File: `main.py`

**Purpose**
Main orchestration entry point and public execution wrappers for the escalation agent.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: get_escalation_graph()

Parameters:
- None

Returns:
- Compiled LangGraph instance

Purpose:
Lazily compiles and caches the main escalation state machine singleton.
```

```
Function: _build_config()

Parameters:
- thread_id : Optional[str]

Returns:
- Dict[str, Any]

Purpose:
Constructs configuration metadata frame carrying the state thread reference.
```

```
Function: _serialize_final_state()

Parameters:
- final_state : Dict[str, Any]
- thread_id : str

Returns:
- Dict[str, Any]

Purpose:
Translates internal graph TypedDict contents into client-facing serialized JSON.
```

```
Function: _extract_interrupt_payload()

Parameters:
- graph : Compiled LangGraph
- config : Dict[str, Any]

Returns:
- Optional[Dict[str, Any]]

Purpose:
Discovers suspended checkpoint interrupt payloads for Human-In-The-Loop review.
```

```
Function: run_escalation_agent()

Parameters:
- payload : Dict[str, Any]

Returns:
- Dict[str, Any]

Purpose:
Validates source agent, hydrates state, runs the LangGraph workflow, and returns a structured result.
```

```
Function: resume_escalation_review()

Parameters:
- thread_id : str
- decision : Dict[str, Any]

Returns:
- Dict[str, Any]

Purpose:
Feeds a manual governance response payload back to a suspended graph checkpoint via Command(resume=).
```

**Constants**
- `ALLOWED_SOURCE_AGENTS` : `Set[str]`
- `_GRAPH` : singleton (initially `None`)

---

### File: `test_escalation_agent_suite.py`

**Purpose**
Integration test suite executing QA verification cases against the relational database environment.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: prepare_env()

Parameters:
- ticket_id : str
- customer_id : int

Returns:
- None

Purpose:
Purges old case data and seeds relational database records to satisfy FK constraint checks before each test.
```

```
Function: build_payload()

Parameters:
- ticket_id : Any
- customer_id : Any
- message : str
- source_agent : str (default "triage_agent")

Returns:
- dict

Purpose:
Generates standardized payload structures modeling upstream caller messages.
```

```
Function: test_category_7()

Parameters:
- None

Returns:
- None

Purpose:
Verifies graceful degradation when customer IDs are missing from the database.
```

```
Function: test_category_8()

Parameters:
- None

Returns:
- None

Purpose:
Stress tests with empty logs, large character payloads, and bulk sequential execution loops.
```

**Constants:** None

---

### File: `test_escalation_agent.ipynb`

**Purpose**
Interactive scratchpad notebook for graph compilation, payload testing, and HITL resumption testing.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions** (Jupyter cells)
- `build_payload()` — constructs test payload dictionaries
- `build_state()` — wraps `EscalationStateFactory.from_payload()`
- `run_case()` — runs graph.invoke() on a constructed state
- `resume_case()` — resumes a suspended graph checkpoint via `Command(resume=decision)`

**Constants:** None

---

## config/ Directory

---

### File: `config/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `config/constants.py`

**Purpose**
Empty configuration constants placeholder file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

## db/ Directory

---

### File: `db/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `db/session.py`

**Purpose**
SQLAlchemy engine configuration and session provider lifecycle manager.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: get_db()

Parameters:
- None

Returns:
- Generator[Session, None, None]

Purpose:
Yields a contextual local transaction session and handles closing on teardown.
```

**Constants**
- `DB_USER` : `str` (from env)
- `DB_PASS` : `str` (from env, required)
- `DB_HOST` : `str` (from env, default `"localhost"`)
- `DB_PORT` : `str` (from env, default `"5432"`)
- `DB_NAME` : `str` (from env, default `"customer_support_ai"`)
- `DATABASE_URL` : `str`
- `engine` : SQLAlchemy Engine
- `SessionLocal` : SQLAlchemy Sessionmaker

---

## factories/ Directory

---

### File: `factories/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `factories/state_factory.py`

**Purpose**
Normalizes unstructured upstream caller payloads into a fully initialized `EscalationState`.

**Classes**

```
Class: EscalationStateFactory
Type: Manager / Utility

Methods:
- @staticmethod from_payload(payload: Dict[str, Any]) -> EscalationState

Purpose:
Validates source agent, normalizes types, and constructs a complete EscalationState dict.
```

**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: safe_float()

Parameters:
- value : Any
- default : float (default 0.0)

Returns:
- float

Purpose:
Safe coercion utility wrapping float casts with fallback.
```

```
Function: safe_int()

Parameters:
- value : Any
- default : int (default 0)

Returns:
- int

Purpose:
Safe coercion utility wrapping integer casts with fallback.
```

**Constants**
- `VALID_ESCALATION_SOURCES` : `Set[str]`

**Relationships**
- Consumes: `EscalationState`
- Used By: `main.py`, `services/escalation_agent.py`

---

## graph/ Directory

---

### File: `graph/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `graph/escalation_graph.py`

**Purpose**
Assembles the full LangGraph state machine topology and configures node pathways.

**LangGraph Components**

```
State Object:
- EscalationState

Nodes:
- validate_contract
- trigger_assessment
- customer_context
- conversation_context
- risk_scoring
- routing_decision
- holding_response
- brief_generation
- human_review
- notification_dispatch
- case_persistence
- response
- dev_auto_approve (only when enable_hitl=False)

Routers:
- route_validation  (after validate_contract → "valid" / "invalid")
- route_duplicate_case  (after trigger_assessment → "duplicate" / "continue")

Entry Point:
- validate_contract

Exit Point:
- response → END
```

**Classes:** None

**Functions**

```
Function: dev_auto_approve_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Injects a mock APPROVE HumanDecision to bypass the human_review gate in local/dev mode.
```

```
Function: build_escalation_graph()

Parameters:
- enable_hitl : bool (default True)

Returns:
- Compiled LangGraph StateGraph app

Purpose:
Registers all nodes, conditional edges, deterministic edges, and compiles with MemorySaver checkpointer.
```

**Constants:** None

**Relationships**
- Consumes: All node functions, `EscalationState`, `HumanDecision`, `route_validation`, `route_duplicate_case`
- Produces: Compiled LangGraph `app`

---

### File: `graph/routers.py`

**Purpose**
Implements conditional routing checks directing graph branch decisions.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: route_validation()

Parameters:
- state : EscalationState

Returns:
- str  ("valid" or "invalid")

Purpose:
Routes to trigger_assessment if no errors exist; routes to response on validation failure.
```

```
Function: route_duplicate_case()

Parameters:
- state : EscalationState

Returns:
- str  ("duplicate" or "continue")

Purpose:
Inspects trigger_assessment.duplicate_case_detected; hydrates response and routes to response on duplicate.
```

**Constants:** None

---

## mapper/ Directory

---

### File: `mapper/escalation_final_responce.py`

**Purpose**
Translates internal state variables into the public `EscalationAgentResponse` output model.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: build_escalation_output()

Parameters:
- final_state : dict
- thread_id : str | None
- review_payload : dict | None
- error : str | None

Returns:
- EscalationAgentResponse

Purpose:
Hydrates the API output container from evaluated LangGraph state variables.
```

**Constants:** None

**Relationships**
- Consumes: `EscalationAgentResponse`
- Produces: `EscalationAgentResponse`

---

## nodes/ Directory

---

### File: `nodes/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `nodes/brief_generation_node.py`

**Purpose**
Graph node that generates an LLM-assisted human handoff intelligence brief.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: _map_emotional_state()

Parameters:
- sentiment : str

Returns:
- EmotionalState

Purpose:
Maps raw sentiment string values to EmotionalState enum members.
```

```
Function: brief_generation_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Invokes HumanBriefService with enriched context; falls back to a structured degradation brief on failure.
```

**Constants:** None

**Relationships**
- Consumes: `HumanBriefService`, `get_llm_client`, `CustomerContext`, `ConversationContext`, `TriggerAssessment`, `RiskAssessment`, `RoutingDecision`
- Produces: `HumanBrief` (written to `state["human_brief"]`)

---

### File: `nodes/case_persistence_node.py`

**Purpose**
Transactional node committing escalation data, audit events, and notifications atomically.

**Database**
- PostgreSQL

**Tables Referenced**
- `escalation_cases`
- `escalation_audit`
- `notification_outbox`

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: case_persistence_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Coordinates EscalationRepository, AuditRepository, NotificationOutboxRepository in a single atomic session commit.
```

**Constants:** None

**Relationships**
- Consumes: `EscalationRepository`, `AuditRepository`, `NotificationOutboxRepository`, `get_db`
- Used By: `graph/escalation_graph.py`

---

### File: `nodes/conversation_context_node.py`

**Purpose**
Assembles conversation transcripts, extracted agent actions, and failure analysis.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: conversation_context_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Calls ConversationRepository to build transcripts and extract actions from workflow logs.
```

```
Function: _extract_failure_reasons()

Parameters:
- workflow_logs : List[Dict[str, Any]]

Returns:
- List[str]

Purpose:
Scans message/data fields in logs to identify FailureReason keywords deterministically.
```

**Constants:** None

**Relationships**
- Consumes: `ConversationRepository`, `ConversationContext`, `FailureReason`
- Produces: `ConversationContext` (written to `state["conversation_context"]`)

---

### File: `nodes/customer_context_node.py`

**Purpose**
Hydrates customer CRM intelligence including tier, LTV, escalation history, and sentiment trend.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: _normalize_customer_tier()

Parameters:
- subscription_plan : str | None
- profile_tier : str | None

Returns:
- str

Purpose:
Normalizes raw plan/tier labels into standard business tier strings (enterprise, premium_plus, premium, standard).
```

```
Function: customer_context_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Queries CustomerRepository and TicketRepository to resolve tier, LTV, repeat counts, and sentiment trend.
```

**Constants:** None

**Relationships**
- Consumes: `CustomerRepository`, `TicketRepository`, `CustomerContext`
- Produces: `CustomerContext` (written to `state["customer_context"]`)

---

### File: `nodes/holding_response_node.py`

**Purpose**
Generates the customer-facing holding message to acknowledge escalation.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: holding_response_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Invokes HoldingResponseService; falls back to a safe static message on failure or missing context.
```

**Constants:** None

**Relationships**
- Consumes: `HoldingResponseService`, `RiskAssessment`, `RoutingDecision`, `TriggerAssessment`, `CustomerContext`
- Produces: `state["holding_message"]` : `str`

---

### File: `nodes/human_review_node.py`

**Purpose**
Human governance checkpoint — suspends graph execution for manual review or auto-approves.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: human_review_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Evaluates governance policy rules; calls interrupt() for critical/VIP cases; auto-approves otherwise.
```

**Constants:** None

**Relationships**
- Consumes: `HumanDecision`, `HumanDecisionType`, LangGraph `interrupt()`
- Produces: `state["human_decision"]` : `HumanDecision`, `state["review_required"]` : `bool`

---

### File: `nodes/notification_dispatch_node.py`

**Purpose**
Builds and stages outbox-ready notification job payloads for approved escalations.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: notification_dispatch_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Validates governance approval then calls NotificationService.build_jobs() to stage alert payloads.
```

**Constants:** None

**Relationships**
- Consumes: `NotificationService`, `HumanDecision`, `HumanBrief`, `RoutingDecision`, `RiskAssessment`, `CustomerContext`, `TriggerAssessment`
- Produces: `state["notification_jobs"]` : `List[NotificationJob]`

---

### File: `nodes/response_node.py`

**Purpose**
Serializes resolved workflow state properties to the final public API output.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: response_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Generates EscalationResponse with ESCALATED or DUPLICATE_SUPPRESSED status.
```

**Constants:** None

**Relationships**
- Consumes: `EscalationResponse`, `RiskAssessment`, `RoutingDecision`, `TriggerAssessment`
- Produces: `state["response"]` : `EscalationResponse`

---

### File: `nodes/risk_scoring_node.py`

**Purpose**
Calculates quantitative risk score and severity level using workflow triage signals.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: risk_scoring_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Validates required context then invokes RiskEngine.assess() to produce a RiskAssessment.
```

**Constants:** None

**Relationships**
- Consumes: `RiskEngine`, `TriggerAssessment`, `CustomerContext`, `ConversationContext`
- Produces: `state["risk_assessment"]` : `RiskAssessment`

---

### File: `nodes/routing_decision_node.py`

**Purpose**
Determines human queue assignment and SLA resolution deadline.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: routing_decision_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Validates required context then invokes RoutingService.decide() to produce a RoutingDecision.
```

**Constants:** None

**Relationships**
- Consumes: `RoutingService`, `TriggerAssessment`, `RiskAssessment`, `CustomerContext`
- Produces: `state["routing_decision"]` : `RoutingDecision`

---

### File: `nodes/sla_tracking_node.py`

**Purpose**
Empty SLA background tracking node placeholder.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `nodes/trigger_assessment_node.py`

**Purpose**
Performs trigger classification and active duplicate case detection.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: trigger_assessment_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Runs TriggerEngine.assess() and queries EscalationRepository for active duplicate cases.
```

**Constants:** None

**Relationships**
- Consumes: `TriggerEngine`, `EscalationRepository`, `get_db`
- Produces: `state["trigger_assessment"]` : `TriggerAssessment`

---

### File: `nodes/validate_contract_node.py`

**Purpose**
Fail-fast schema validation node that aborts execution on missing required fields.

**Classes:** None
**Schemas / Models:** None
**Enums:** None

**Functions**

```
Function: validate_contract_node()

Parameters:
- state : EscalationState

Returns:
- EscalationState

Purpose:
Checks ticket_id, customer_id, source_agent, and ticket message content; raises ValueError on failure.
```

**Constants:** None

---

## prompts/ Directory

---

### File: `prompts/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `prompts/escalation_brief_prompt.py`

**Purpose**
Empty prompts placeholder file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

## repositories/ Directory

---

### File: `repositories/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `repositories/agent_action_repository.py`

**Purpose**
Empty repository placeholder file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `repositories/audit_repository.py`

**Purpose**
Manages transactional writes and reads for the immutable escalation audit log.

**Database:** PostgreSQL
**Tables Referenced:** `escalation_audit`

**Classes**

```
Class: AuditRepository
Type: Repository

Methods:
- __init__(session: Session)
- log_event(case_id: str, ticket_id: Optional[str], event_type: AuditEventType, payload: Dict[str, Any], operator_type: OperatorType = OperatorType.AI) -> bool
- get_case_audit(case_id: str) -> List[Dict[str, Any]]
- get_ticket_audit(ticket_id: str) -> List[Dict[str, Any]]

Purpose:
Logs audit events inside nested savepoint transactions; read methods fetch full audit trails.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

**Relationships**
- Consumes: `AuditEventType`, `OperatorType`
- Used By: `nodes/case_persistence_node.py`

---

### File: `repositories/conversation_repository.py`

**Purpose**
Reconstructs conversation transcripts and extracts structured agent actions.

**Database:** PostgreSQL
**Tables Referenced:** `tickets`

**Classes**

```
Class: ConversationRepository
Type: Repository

Methods:
- __init__(session: Session)
- build_conversation_transcript(ticket_id: str, current_message: str, workflow_logs: List[Dict[str, Any]]) -> str
- extract_agent_actions(workflow_logs: List[Dict[str, Any]], source_agent: str) -> List[Dict[str, Any]]
- get_recent_ticket_history(customer_id: int, limit: int = 5) -> List[Dict[str, Any]]

Purpose:
Assembles sorted transcript lines from logs; filters noise nodes when extracting agent actions.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `NOISE_NODES` : `Set[str]`

**Relationships**
- Used By: `nodes/conversation_context_node.py`

---

### File: `repositories/customer_repository.py`

**Purpose**
Retrieves account profiles, subscription details, billing history, and escalation history.

**Database:** PostgreSQL
**Tables Referenced:** `customers`, `subscriptions`, `orders`, `escalation_cases`

**Classes**

```
Class: CustomerRepository
Type: Repository

Methods:
- __init__(session: Session)
- @staticmethod _sanitize_limit(limit: int) -> int
- get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]
- get_customer_by_email(email: str) -> Optional[Dict[str, Any]]
- get_customer_subscription(customer_id: int) -> Optional[Dict[str, Any]]
- get_billing_history(customer_id: int, limit: int = 5) -> List[Dict[str, Any]]
- get_escalation_history(customer_id: int, limit: int = 5) -> List[Dict[str, Any]]

Purpose:
Read-only lookups against customer tables for enrichment data.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

**Relationships**
- Used By: `nodes/customer_context_node.py`

---

### File: `repositories/escalation_repository.py`

**Purpose**
Maintains persistence lifecycle of escalation case records.

**Database:** PostgreSQL
**Tables Referenced:** `escalation_cases`

**Classes**

```
Class: EscalationRepository
Type: Repository

Methods:
- __init__(session: Session)
- _execute_mutation(query, params: Dict[str, Any], error_message: str) -> bool
- create_case(case_id: str, ticket_id: str, customer_id: int, source_agent: str, trigger_assessment: dict, risk_assessment: dict, human_brief: dict, routing_decision: dict, holding_message: str = None)
- find_active_duplicate_case(ticket_id: str, customer_id: int) -> Optional[Dict[str, Any]]
- get_case(case_id: str) -> Optional[Dict[str, Any]]
- update_case_status(case_id: str, new_status: str) -> bool
- resolve_case(case_id: str) -> bool

Purpose:
Inserts new escalation cases; finds active duplicates; updates status and resolution timestamps.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `VALID_CASE_STATUSES` : `Set[str]`

**Relationships**
- Used By: `nodes/case_persistence_node.py`, `nodes/trigger_assessment_node.py`

---

### File: `repositories/notification_outbox_repository.py`

**Purpose**
Manages staging, fetching, and lifecycle state updates of the notification outbox.

**Database:** PostgreSQL
**Tables Referenced:** `notification_outbox`

**Classes**

```
Class: NotificationOutboxRepository
Type: Repository

Methods:
- __init__(session: Session)
- _execute_mutation(query, params: Dict[str, Any], error_message: str) -> bool
- enqueue_job(job: NotificationJob) -> bool
- enqueue_notification(case_id: str, channel: str, recipient: str, payload: Dict[str, Any]) -> bool
- fetch_pending_notifications(limit: int = 10) -> List[Dict[str, Any]]
- get_case_notifications(case_id: str) -> List[Dict[str, Any]]
- mark_processing(notification_id: int) -> bool
- mark_sent(notification_id: int) -> bool
- mark_failed(notification_id: int, error_message: str) -> bool

Purpose:
Stages queued outbound jobs and tracks delivery success metrics per channel.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

**Relationships**
- Consumes: `NotificationJob`
- Used By: `nodes/case_persistence_node.py`

---

### File: `repositories/ticket_repository.py`

**Purpose**
Queries the tickets table for ticket details, history, repeat counts, and sentiment.

**Database:** PostgreSQL
**Tables Referenced:** `tickets`

**Classes**

```
Class: TicketRepository
Type: Repository

Methods:
- __init__(session: Session)
- @staticmethod _sanitize_limit(limit: int) -> int
- get_ticket_by_id(ticket_id: str) -> Optional[Dict[str, Any]]
- get_recent_tickets(customer_id: int, limit: int = 5) -> List[Dict[str, Any]]
- count_repeat_issues(customer_id: int, issue_type: str) -> int
- count_unresolved_tickets(customer_id: int) -> int
- get_last_ticket_sentiment(customer_id: int) -> Optional[str]

Purpose:
Resolves repeat issue counts, unresolved ticket counts, and last logged sentiment values.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

**Relationships**
- Used By: `nodes/customer_context_node.py`

---

## schemas/ Directory

---

### File: `schemas/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `schemas/audit_record.py`

**Purpose**
Defines models and enumerations for capturing immutable audit event records.

**Classes:** None

**Schemas / Models**

```
Schema: AuditRecord (Pydantic Model)

Fields:
- case_id         : str
- ticket_id       : Optional[str]  (default None)
- event_type      : AuditEventType
- payload         : Dict[str, Any] (default dict)
- operator_type   : OperatorType   (default OperatorType.AI)

Purpose:
Holds metadata describing a single executed workflow step.
```

**Enums**

```
Enum: AuditEventType

Values:
- TRIGGER_DETECTED       = "trigger_detected"
- DUPLICATE_DETECTED     = "duplicate_detected"
- RISK_SCORED            = "risk_scored"
- HOLDING_SENT           = "holding_sent"
- BRIEF_GENERATED        = "brief_generated"
- ROUTING_COMPLETED      = "routing_completed"
- NOTIFICATION_ENQUEUED  = "notification_enqueued"
- CASE_RESOLVED          = "case_resolved"
- CASE_CLOSED            = "case_closed"
- ERROR                  = "error"

Purpose:
Standard categorization labels for audit log entries.
```

```
Enum: OperatorType

Values:
- AI     = "AI"
- HUMAN  = "HUMAN"
- SYSTEM = "SYSTEM"

Purpose:
Classifies the entity performing the logged action.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/conversation_context.py`

**Purpose**
Defines structures modeling conversation transcripts and prior agent actions.

**Classes:** None

**Schemas / Models**

```
Schema: AgentAction (Pydantic Model)

Fields:
- agent_name : str
- action     : str
- result     : str
- metadata   : Dict[str, Any] (default dict)

Purpose:
Captures the outcome of a single action step performed by an agent.
```

```
Schema: ConversationContext (Pydantic Model)

Fields:
- conversation_transcript : str
- agent_actions_taken     : List[AgentAction] (default list)
- failure_reasons         : List[FailureReason] (default list)
- knowledge_gap_detected  : bool (default False)

Purpose:
Aggregates gathered conversational support evidence for the human brief.
```

**Enums**

```
Enum: FailureReason

Values:
- KNOWLEDGE_GAP_DETECTED           = "knowledge_gap_detected"
- LOW_CONFIDENCE                   = "low_confidence"
- POLICY_CONFLICT                  = "policy_conflict"
- FRAUD_SUSPICION                  = "fraud_suspicion"
- IDENTITY_VERIFICATION_FAILED     = "identity_verification_failed"
- TAKEOVER_SUSPICION               = "takeover_suspicion"
- MANUAL_REVIEW_REQUIRED           = "manual_review_required"
- SLA_BREACH_IMMINENT              = "sla_breach_imminent"
- DUPLICATE_ESCALATION_DETECTED    = "duplicate_escalation_detected"

Purpose:
Identifies specific reasons automation was blocked from resolving the issue.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/customer_context.py`

**Purpose**
CRM customer profiles, tier classification, and sentiment variables.

**Classes:** None

**Schemas / Models**

```
Schema: CustomerContext (Pydantic Model)

Fields:
- customer_id                 : int
- customer_name               : str
- customer_email              : str
- customer_tier               : CustomerTier     (default STANDARD)
- ltv                         : float            (default 0.0, ge=0.0)
- total_past_tickets          : int              (default 0, ge=0)
- total_past_escalations      : int              (default 0, ge=0)
- repeat_issue_count          : int              (default 0, ge=0)
- historical_sentiment_trend  : SentimentTrend   (default NEUTRAL)

Purpose:
Models account value, tier, and historical behavior for risk profiling.
```

**Enums**

```
Enum: CustomerTier

Values:
- BASIC        = "basic"
- STANDARD     = "standard"
- PREMIUM      = "premium"
- PREMIUM_PLUS = "premium_plus"
- ENTERPRISE   = "enterprise"

Purpose:
Business support SLA priority tiers.
```

```
Enum: SentimentTrend

Values:
- POSITIVE   = "positive"
- NEUTRAL    = "neutral"
- FRUSTRATED = "frustrated"
- ANGRY      = "angry"
- MIXED      = "mixed"

Purpose:
Classifies rolling customer emotional trend from historical tickets.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/escalation_output.py`

**Purpose**
Top-level public API output schema representing the final execution state.

**Classes:** None

**Schemas / Models**

```
Schema: EscalationAgentResponse (Pydantic Model)

Fields:
- ticket_id       : str
- source_agent    : str
- status          : str
- thread_id       : Optional[str]               (default None)
- response        : Optional[EscalationResponse] (default None)
- review_payload  : Optional[dict[str, Any]]    (default None)
- error           : Optional[str]               (default None)

Purpose:
Envelope for API responses returned to upstream callers.
```

**Enums:** None | **Functions:** None | **Constants:** None

---

### File: `schemas/escalation_response.py`

**Purpose**
Structured fields carrying workflow resolution outcomes.

**Classes:** None

**Schemas / Models**

```
Schema: EscalationResponse (Pydantic Model)

Fields:
- status          : EscalationStatus
- case_id         : str | None       (default None)
- priority        : RiskLevel | None (default None)
- assigned_team   : str | None       (default None)
- holding_sent    : bool             (default False)
- error_message   : str | None       (default None)

Purpose:
Key triage decisions returned on workflow completion.
```

**Enums**

```
Enum: EscalationStatus

Values:
- ESCALATED            = "ESCALATED"
- DUPLICATE_SUPPRESSED = "DUPLICATE_SUPPRESSED"
- FAILED               = "FAILED"

Purpose:
Final classification status of the escalation workflow run.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/escalation_state.py`

**Purpose**
Main TypedDict defining the complete state structure carried across all graph steps.

**Classes:** None

**Schemas / Models**

```
Schema: EscalationState (TypedDict)

Fields:
- ticket                  : Dict[str, Any]
- ticket_id               : str
- customer_id             : int
- customer_email          : str
- source_agent            : str
- initial_intent          : str
- initial_sentiment       : str
- initial_urgency         : str
- supervisor_confidence   : float
- entities                : List[Dict[str, Any]]
- workflow_logs           : List[Dict[str, Any]]
- trigger_assessment      : Optional[TriggerAssessment]
- customer_context        : Optional[CustomerContext]
- conversation_context    : Optional[ConversationContext]
- risk_assessment         : Optional[RiskAssessment]
- holding_message         : Optional[str]
- holding_sent            : bool
- human_brief             : Optional[HumanBrief]
- routing_decision        : Optional[RoutingDecision]
- review_required         : bool
- review_completed        : bool
- human_decision          : Optional[HumanDecision]
- case_id                 : Optional[str]
- notification_jobs       : List[NotificationJob]
- response                : Optional[EscalationResponse]
- current_node            : str
- errors                  : List[str]
- metrics                 : Dict[str, Any]
- audit_status            : Optional[str]

Purpose:
Global context map tracking all state updates across the LangGraph execution topology.
```

**Enums:** None | **Functions:** None | **Constants:** None

---

### File: `schemas/human_brief.py`

**Purpose**
Summarized customer intelligence packet prepared for human agent reviewers.

**Classes:** None

**Schemas / Models**

```
Schema: HumanBrief (Pydantic Model)

Fields:
- customer_summary        : str
- issue_summary           : str
- emotional_state         : EmotionalState
- churn_risk_level        : ChurnRiskLevel
- churn_reason            : str
- attempted_actions       : List[str]
- blockers                : List[str]
- recommended_next_action : str
- urgency_reason          : str
- brief_confidence        : float  (ge=0.0, le=1.0)

Purpose:
Narrative handoff summary reviewed in human support queues.
```

**Enums**

```
Enum: EmotionalState

Values:
- ANGRY      = "angry"
- FRUSTRATED = "frustrated"
- NEUTRAL    = "neutral"
- POSITIVE   = "positive"
- URGENT     = "urgent"
- HOSTILE    = "hostile"

Purpose:
Maps current customer emotional posture.
```

```
Enum: ChurnRiskLevel

Values:
- LOW      = "LOW"
- MEDIUM   = "MEDIUM"
- HIGH     = "HIGH"
- CRITICAL = "CRITICAL"

Purpose:
Maps estimated customer attrition likelihood.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/human_decision.py`

**Purpose**
Represents governance review decisions returned to release graph execution suspensions.

**Classes:** None

**Schemas / Models**

```
Schema: HumanDecision (Pydantic Model)

Fields:
- decision          : HumanDecisionType
- reviewer_id       : str
- notes             : Optional[str]  (default None)
- override_team     : Optional[str]  (default None)
- override_priority : Optional[str]  (default None)

Purpose:
Captures human reviewer instructions targeting queue or priority adjustments.
```

**Enums**

```
Enum: HumanDecisionType

Values:
- APPROVE  = "approve"
- REJECT   = "reject"
- OVERRIDE = "override"
- HOLD     = "hold"

Purpose:
Evaluated reviewer governance actions.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/notification_job.py`

**Purpose**
Outbox job records scheduled for delivery by async dispatch workers.

**Classes:** None

**Schemas / Models**

```
Schema: NotificationJob (Pydantic Model)

Fields:
- case_id      : str
- channel      : NotificationChannel
- recipient    : str
- payload      : Dict[str, Any]
- status       : NotificationStatus (default PENDING)
- retry_count  : int                (default 0, ge=0)
- last_error   : Optional[str]      (default None)

Purpose:
Models queued outgoing channel alert records for the outbox table.
```

**Enums**

```
Enum: NotificationChannel

Values:
- DASHBOARD = "dashboard"
- EMAIL     = "email"
- SLACK     = "slack"
- TELEGRAM  = "telegram"
- PAGER     = "pager"

Purpose:
Delivery target channel protocols.
```

```
Enum: NotificationStatus

Values:
- PENDING    = "pending"
- PROCESSING = "processing"
- SENT       = "sent"
- FAILED     = "failed"

Purpose:
Execution state tracking for outbox delivery.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/risk_assessment.py`

**Purpose**
Risk calculation result carrying numeric score and categorical severity flags.

**Classes:** None

**Schemas / Models**

```
Schema: RiskAssessment (Pydantic Model)

Fields:
- score          : float    (ge=0.0, le=100.0)
- level          : RiskLevel
- legal_risk     : bool     (default False)
- security_risk  : bool     (default False)
- churn_risk     : bool     (default False)
- sla_risk       : bool     (default False)

Purpose:
Severity classification carrying specialized queue routing flags.
```

**Enums**

```
Enum: RiskLevel

Values:
- LOW      = "low"
- MEDIUM   = "medium"
- HIGH     = "high"
- CRITICAL = "critical"

Purpose:
Standard severity ranges for escalation triage.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/routing_decision.py`

**Purpose**
Queue assignment and SLA deadline results from the routing engine.

**Classes:** None

**Schemas / Models**

```
Schema: RoutingDecision (Pydantic Model)

Fields:
- assigned_team                : str
- target_queue                 : str
- risk_level                   : EscalationPriority  (alias: risk_level)
- sla_deadline                 : datetime
- routing_reason               : str
- requires_immediate_attention : bool  (default False)

Purpose:
Actionable routing metadata directing queue distribution and SLA enforcement.
```

**Enums**

```
Enum: EscalationPriority

Values:
- LOW      = "low"
- MEDIUM   = "medium"
- HIGH     = "high"
- CRITICAL = "critical"

Purpose:
Urgent triage priority classifications.
```

**Functions:** None | **Constants:** None

---

### File: `schemas/trigger_assessment.py`

**Purpose**
Classification signals and duplicate detection results from ticket parsing.

**Classes:** None

**Schemas / Models**

```
Schema: TriggerAssessment (Pydantic Model)

Fields:
- category                : TriggerCategory       (alias: trigger_category)
- reasons                 : List[TriggerReason]   (alias: trigger_reasons)
- duplicate_case_detected : bool                  (default False)
- existing_case_id        : Optional[str]         (default None, alias: duplicate_of_case_id)

Purpose:
Captures primary category groupings, specific reason signals, and duplicate case references.
```

**Enums**

```
Enum: TriggerCategory

Values:
- LEGAL         = "legal"
- SECURITY      = "security"
- CHURN         = "churn"
- SLA           = "sla"
- KNOWLEDGE_GAP = "knowledge_gap"
- MANUAL_REVIEW = "manual_review"
- REPEAT_ISSUE  = "repeat_issue"
- OPERATIONAL   = "operational"
- GENERAL       = "general"

Purpose:
Primary groupings of escalation trigger checks.
```

```
Enum: TriggerReason

Values:
- LEGAL_LANGUAGE                = "legal_language"
- VIP_AT_RISK                   = "vip_at_risk"
- TAKEOVER_SUSPICION            = "takeover_suspicion"
- IDENTITY_VERIFICATION_FAILED  = "identity_verification_failed"
- KNOWLEDGE_GAP_DETECTED        = "knowledge_gap_detected"
- LOW_CONFIDENCE                = "low_confidence"
- HIGH_VALUE_REFUND             = "high_value_refund"
- POLICY_CONFLICT               = "policy_conflict"
- SLA_BREACH_IMMINENT           = "sla_breach_imminent"
- REPEAT_ISSUE_DETECTED         = "repeat_issue_detected"
- DUPLICATE_ESCALATION_DETECTED = "duplicate_escalation_detected"
- CHURN_THREAT                  = "churn_threat"
- HOSTILE_LANGUAGE              = "hostile_language"
- FRAUD_SUSPICION               = "fraud_suspicion"
- ACCOUNT_ABUSE_DETECTED        = "account_abuse_detected"

Purpose:
Specific keyword-matching signals detected in ticket messages and workflow logs.
```

**Functions:** None | **Constants:** None

---

## services/ Directory

---

### File: `services/__init__.py`

**Purpose**
Module initialization file.

**Classes:** None | **Schemas:** None | **Enums:** None | **Functions:** None | **Constants:** None

---

### File: `services/brief_generation_service.py`

**Purpose**
Combines quantitative telemetry with LLM narrative generation to write human handoff summaries.

**Classes**

```
Class: HumanBriefService
Type: Service

Methods:
- __init__(llm_client: Any)
- generate(customer_context: CustomerContext, conversation_context: ConversationContext, trigger_assessment: TriggerAssessment, risk_assessment: RiskAssessment, routing_decision: RoutingDecision, current_sentiment: str = "neutral") -> HumanBrief
- _build_customer_summary(customer: CustomerContext) -> str
- _build_emotional_state(sentiment: str) -> EmotionalState
- _derive_churn_risk_level(risk: RiskAssessment, emotional_state: EmotionalState) -> ChurnRiskLevel
- _extract_attempted_actions(conversation: ConversationContext) -> List[str]
- _extract_blockers(trigger: TriggerAssessment, conversation: ConversationContext) -> List[str]
- _build_urgency_reason(risk: RiskAssessment, trigger: TriggerAssessment, customer: CustomerContext) -> str
- _truncate_transcript(transcript: str) -> str
- _safe_parse_llm_json(raw_text: str) -> Dict[str, str]
- _generate_llm_summary(conversation_context: ConversationContext, trigger_assessment: TriggerAssessment, risk_assessment: RiskAssessment, routing_decision: RoutingDecision) -> Dict[str, str]

Purpose:
Orchestrates structured summaries using weight metrics and a Groq LLM call.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `MAX_TRANSCRIPT_CHARS` : `5000`
- `MAX_ACTIONS` : `5`

**Relationships**
- Consumes: `CustomerContext`, `ConversationContext`, `TriggerAssessment`, `RiskAssessment`, `RoutingDecision`, LLM client
- Produces: `HumanBrief`
- Used By: `nodes/brief_generation_node.py`

---

### File: `services/escalation_agent.py`

**Purpose**
Internal service provider mirroring the main.py entry point logic (used by the test suite).

**Classes:** None

**Functions**

```
Function: get_escalation_graph()

Parameters:
- None

Returns:
- Compiled LangGraph StateGraph

Purpose:
Lazily compiles and caches the escalation graph with enable_hitl=True.
```

```
Function: _build_config()

Parameters:
- thread_id : Optional[str]

Returns:
- Dict[str, Any]

Purpose:
Builds configurable thread execution context.
```

```
Function: _serialize_final_state()

Parameters:
- final_state : Dict[str, Any]
- thread_id : str

Returns:
- Dict[str, Any]

Purpose:
Translates final graph state into a clean JSON-serializable response.
```

```
Function: run_escalation_agent()

Parameters:
- payload : Dict[str, Any]

Returns:
- Dict[str, Any]

Purpose:
Validates source agent, hydrates state, streams graph, detects interrupts, and returns result.
```

```
Function: resume_escalation_review()

Parameters:
- thread_id : str
- decision : Dict[str, Any]

Returns:
- Dict[str, Any]

Purpose:
Resumes a paused graph checkpoint by feeding a human decision via Command(resume=).
```

**Constants**
- `ALLOWED_SOURCE_AGENTS` : `Set[str]`
- `_GRAPH` : singleton (initially `None`)

---

### File: `services/holding_response_service.py`

**Purpose**
Resolves template texts informing customers that their issue has been escalated for specialist review.

**Classes**

```
Class: HoldingResponseService
Type: Service

Methods:
- _select_template(category: str, risk_level: str, customer_tier: str) -> str
- generate(risk_assessment: RiskAssessment, routing_decision: RoutingDecision, trigger_assessment: TriggerAssessment, customer_context: CustomerContext, channel: str = "chat") -> str

Purpose:
Returns the appropriate holding message template based on risk level, category, and customer tier.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None
**Constants:** None

**Relationships**
- Consumes: `RiskAssessment`, `RoutingDecision`, `TriggerAssessment`, `CustomerContext`
- Produces: `str` holding message
- Used By: `nodes/holding_response_node.py`

---

### File: `services/notification_service.py`

**Purpose**
Determines target alert distribution channels and builds delivery payloads for each channel.

**Classes**

```
Class: NotificationService
Type: Service

Methods:
- build_jobs(case_id: str, ticket_id: str, human_brief: HumanBrief, routing_decision: RoutingDecision, risk_assessment: RiskAssessment, customer_context: CustomerContext, trigger_assessment: TriggerAssessment) -> List[NotificationJob]
- _select_channels(risk_level: str, category: str, risk_assessment: RiskAssessment, customer_tier: str) -> List[NotificationChannel]
- _resolve_recipient(team: str, channel: str) -> str
- _truncate(text: str, max_len: int) -> str
- _build_dashboard_payload(case_id: str, ticket_id: str, assigned_team: str, brief: HumanBrief, risk_level: str) -> Dict[str, Any]
- _build_slack_payload(case_id: str, assigned_team: str, brief: HumanBrief, risk_level: str) -> Dict[str, Any]
- _build_email_payload(case_id: str, ticket_id: str, brief: HumanBrief, risk_level: str) -> Dict[str, Any]
- _build_pager_payload(case_id: str, category: str, risk_level: str) -> Dict[str, Any]

Purpose:
Maps team destinations to channel recipients; constructs structured payloads per channel type.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `MAX_SLACK_TEXT` : `2000`
- `MAX_EMAIL_TEXT` : `5000`
- `MAX_PAGER_TEXT` : `300`
- `TEAM_RECIPIENTS` : `Dict[str, Dict[str, str]]`

**Relationships**
- Produces: `List[NotificationJob]`
- Used By: `nodes/notification_dispatch_node.py`

---

### File: `services/risk_engine.py`

**Purpose**
Calculates deterministic numeric risk scores and assigns categorical severity levels.

**Classes**

```
Class: RiskEngine
Type: Service

Methods:
- assess(trigger_assessment: TriggerAssessment, customer_context: CustomerContext, repeat_issue_count: int = 0, current_sentiment: str = "neutral", sla_breached: bool = False, billing_flags: Optional[List[str]] = None) -> RiskAssessment
- _critical_override(category: str, trigger_assessment: TriggerAssessment, customer_context: CustomerContext, repeat_issue_count: int, current_sentiment: str, sla_breached: bool, fraud_detected: bool) -> bool
- _score_trigger(category: str) -> float
- _score_customer_tier(tier) -> float
- _score_ltv(ltv: float) -> float
- _score_escalation_history(count: int) -> float
- _score_repeat_issues(count: int) -> float
- _score_sentiment(sentiment: str) -> float
- _score_billing_risk(billing_flags: List[str]) -> float
- _score_sla(breached: bool) -> float
- _resolve_level(score: float) -> str
- _build_flags(category: str, fraud_detected: bool, high_churn_signals: bool, sla_breached: bool)

Purpose:
Applies weighted scoring across trigger category, tier, LTV, history, sentiment, and SLA breach signals.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `TRIGGER_WEIGHTS` : `Dict[str, float]`
- `TIER_WEIGHTS` : `Dict[str, float]`
- `CRITICAL_OVERRIDE_CATEGORIES` : `Set[str]`

**Relationships**
- Produces: `RiskAssessment`
- Used By: `nodes/risk_scoring_node.py`

---

### File: `services/routing_service.py`

**Purpose**
Resolves target human support team assignments and SLA resolution deadlines.

**Classes**

```
Class: RoutingService
Type: Service

Methods:
- decide(trigger_assessment: TriggerAssessment, risk_assessment: RiskAssessment, customer_context: CustomerContext, source_agent: str) -> RoutingDecision
- _resolve_team(category: str, source_agent: str) -> str
- _resolve_manual_review_team(source_agent: str) -> str
- _resolve_sla_deadline(risk_level: str, customer_tier: str) -> datetime
- _apply_vip_sla_override(base_hours: float, customer_tier: str) -> float

Purpose:
Maps trigger category → ownership team; calculates SLA deadline with VIP acceleration multipliers.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `CATEGORY_TEAM_MAP` : `Dict[str, str]`
- `MANUAL_REVIEW_TEAM_MAP` : `Dict[str, str]`

**Relationships**
- Produces: `RoutingDecision`
- Used By: `nodes/routing_decision_node.py`

---

### File: `services/trigger_engine.py`

**Purpose**
Identifies legal language, security alerts, SLA warnings, and churn signals using regex and log parsing.

**Classes**

```
Class: TriggerEngine
Type: Service

Methods:
- __init__()
- assess(message: str, sentiment: str, source_agent: str, workflow_logs: List[Dict[str, Any]], knowledge_gap_detected: bool = False, repeat_issue_count: int = 0) -> TriggerAssessment
- _detect_legal(message: str) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_security(message: str) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_sla(message: str) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_operational(message: str) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_churn(sentiment: str) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_manual_review(workflow_logs: List[Dict[str, Any]]) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_repeat_issue(repeat_issue_count: int) -> List[Tuple[TriggerCategory, TriggerReason]]
- _detect_knowledge_gap(knowledge_gap_detected: bool) -> List[Tuple[TriggerCategory, TriggerReason]]
- _resolve_priority(detected_triggers, source_agent: str)

Purpose:
Parses ticket messages with compiled regex patterns; resolves primary category by PRIORITY_MAP ordering.
```

**Schemas / Models:** None
**Enums:** None
**Functions:** None

**Constants**
- `PRIORITY_MAP` : `Dict[TriggerCategory, int]`

**Relationships**
- Produces: `TriggerAssessment`
- Used By: `nodes/trigger_assessment_node.py`

---

## tests/ Directory

> All test files in `tests/` are **empty placeholders** at time of analysis.

| File | Status |
|------|--------|
| `tests/test_brief_generation.py` | Empty |
| `tests/test_duplicate_guard.py` | Empty |
| `tests/test_graph_flow.py` | Empty |
| `tests/test_risk_engine.py` | Empty |
| `tests/test_trigger_engine.py` | Empty |

---

## utils/ Directory

> All utility files are **empty placeholders** at time of analysis.

| File | Status |
|------|--------|
| `utils/ids.py` | Empty |
| `utils/logging_utils.py` | Empty |
| `utils/time_utils.py` | Empty |

---

# Section 3: Folder Summary

## Folder Purpose

The `layer_2_escalation_agent/` module implements a state-machine-driven customer support escalation workflow using LangGraph, Pydantic, and SQLAlchemy. It automates input validation, trigger classification, VIP/historical enrichment, risk scoring, human queue routing, template-driven holding responses, multi-channel alert fanout, and atomic database persistence. High-risk actions (critical risk, security/legal categories, VIP customers) are routed through a Human-In-The-Loop checkpoint utilizing LangGraph thread state suspensions and interactive resume mechanics.

---

## Files Included

- **Root:** `main.py`, `dependencies.py`, `__init__.py`, `test_escalation_agent_suite.py`, `test_escalation_agent.ipynb`
- **config:** `constants.py`
- **db:** `session.py`
- **factories:** `state_factory.py`
- **graph:** `escalation_graph.py`, `routers.py`
- **mapper:** `escalation_final_responce.py`
- **nodes:** `validate_contract_node.py`, `trigger_assessment_node.py`, `customer_context_node.py`, `conversation_context_node.py`, `risk_scoring_node.py`, `routing_decision_node.py`, `holding_response_node.py`, `brief_generation_node.py`, `human_review_node.py`, `notification_dispatch_node.py`, `case_persistence_node.py`, `response_node.py`, `sla_tracking_node.py`
- **repositories:** `audit_repository.py`, `conversation_repository.py`, `customer_repository.py`, `escalation_repository.py`, `notification_outbox_repository.py`, `ticket_repository.py`
- **schemas:** `escalation_state.py`, `trigger_assessment.py`, `customer_context.py`, `conversation_context.py`, `risk_assessment.py`, `routing_decision.py`, `human_brief.py`, `human_decision.py`, `notification_job.py`, `escalation_response.py`, `escalation_output.py`, `audit_record.py`
- **services:** `trigger_engine.py`, `risk_engine.py`, `routing_service.py`, `holding_response_service.py`, `brief_generation_service.py`, `notification_service.py`, `escalation_agent.py`

---

## Main Components

**Repositories:**
- `AuditRepository`
- `ConversationRepository`
- `CustomerRepository`
- `EscalationRepository`
- `NotificationOutboxRepository`
- `TicketRepository`

**Services:**
- `HumanBriefService`
- `HoldingResponseService`
- `NotificationService`
- `RiskEngine`
- `RoutingService`
- `TriggerEngine`

**Schemas:**
- `EscalationState`
- `TriggerAssessment`
- `CustomerContext`
- `ConversationContext`
- `RiskAssessment`
- `RoutingDecision`
- `HumanBrief`
- `HumanDecision`
- `NotificationJob`
- `EscalationResponse`
- `EscalationAgentResponse`
- `AuditRecord`
- `AgentAction`

**Enums:**
- `AuditEventType`
- `OperatorType`
- `FailureReason`
- `CustomerTier`
- `SentimentTrend`
- `EscalationStatus`
- `EmotionalState`
- `ChurnRiskLevel`
- `HumanDecisionType`
- `NotificationChannel`
- `NotificationStatus`
- `RiskLevel`
- `EscalationPriority`
- `TriggerCategory`
- `TriggerReason`

**Utilities:**
- `EscalationStateFactory`
- `safe_float()`
- `safe_int()`
- `get_llm_client()`
- `get_db()`

**Graphs:**
- LangGraph escalation workflow (`graph/escalation_graph.py`)

---

## Input / Output

**Input:**
Upstream caller payload dictionary containing:
- `ticket_id` : `str`
- `customer_id` : `int`
- `source_agent` : `str` (must be in allowed set)
- `initial_intent` : `str`
- `initial_sentiment` : `str`
- `initial_urgency` : `str`
- `supervisor_confidence` : `float`
- `entities` : `List[dict]`
- `workflow_logs` : `List[dict]`
- `ticket` : `dict` containing `message_raw` and/or `message_english`

**Output:**
Serialized dictionary containing:
- `status` : `str` — `ESCALATED` / `DUPLICATE_SUPPRESSED` / `HUMAN_REVIEW_REQUIRED` / `FAILED`
- `case_id` : `str` — escalation tracking case identifier
- `thread_id` : `str` — LangGraph checkpoint thread reference
- `response` : `dict` — serialized `EscalationResponse`
- `workflow_logs` : `List[dict]` — chronological execution log
- `review_payload` : `dict` — (only on `HUMAN_REVIEW_REQUIRED`) interrupt payload for human reviewer
- `error` : `str` — (only on `FAILED`) exception message

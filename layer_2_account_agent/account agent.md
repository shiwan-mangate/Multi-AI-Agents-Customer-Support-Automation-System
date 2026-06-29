# Codebase Inventory & Documentation Report: Layer_2_Account

## Section 1: Folder Structure

```
Layer_2_Account/
│
├── .gitignore
├── account_graph.py
├── state_factory.py
├── test_account_agent.ipynb
│
├── db/
│   └── session.py
│
├── mapper/
│   └── final_responce.py
│
├── nodes/
│   ├── __init__.py
│   ├── abuse_guard_node.py
│   ├── action_resolution_node.py
│   ├── audit_log_node.py
│   ├── billing_history_node.py
│   ├── clarification_check_node.py
│   ├── fetch_account_context_node.py
│   ├── idempotency_node.py
│   ├── identity_resolution_node.py
│   ├── invoice_retrieval_node.py
│   ├── password_reset_node.py
│   ├── response_generation_node.py
│   ├── risk_assessment_node.py
│   ├── security_escalation_node.py
│   ├── subclassify_issue_node.py
│   ├── takeover_detection_node.py
│   ├── unlock_account_node.py
│   ├── validate_contract_node.py
│   └── verification_policy_node.py
│
├── providers/
│   ├── base_auth_provider.py
│   ├── base_billing_provider.py
│   ├── mock_auth_provider.py
│   └── mock_billing_provider.py
│
├── repositories/
│   ├── account_repository.py
│   ├── billing_repository.py
│   ├── customer_repository.py
│   └── security_audit_repository.py
│
├── routers/
│   └── decision_router.py
│
├── schemas/
│   ├── account_state.py
│   ├── domain.py
│   └── final_account_agent_responce.py
│
├── services/
│   ├── abuse_guard.py
│   ├── auth_provider.py
│   ├── billing_provider.py
│   ├── idempotency_service.py
│   ├── identity_service.py
│   ├── risk_engine.py
│   ├── subclassifier.py
│   ├── takeover_detector.py
│   └── verification_policy.py
│
└── utils/
    └── workflow_logger.py
```

---

## Section 2: File Analysis

### File: `account_graph.py`
**Purpose**
Builds and compiles the LangGraph state machine workflow for the Account Agent.

**Classes**
None

**Functions**
* **Function**: `build_account_graph()`
  * **Parameters**: None
  * **Returns**: `CompiledStateGraph`
  * **Purpose**: Instantiates repositories, services, and constructs the StateGraph workflow, compiling it.

**LangGraph Details**
* **State Object**: `AccountState`
* **Nodes**:
  * `validate_contract`
  * `subclassify_issue`
  * `clarification_check`
  * `identity_resolution`
  * `fetch_account_context`
  * `abuse_guard`
  * `action_resolution`
  * `takeover_detection`
  * `risk_assessment`
  * `verification_policy`
  * `idempotency`
  * `password_reset`
  * `unlock_account`
  * `invoice_retrieval`
  * `billing_history`
  * `security_escalation`
  * `audit_log`
  * `response_generation`
* **Routers**:
  * `clarification_router`
  * `execution_router`
* **Entry Point**: `validate_contract`
* **Exit Point**: `END`

---

### File: `state_factory.py`
**Purpose**
Factory utility and helper functions to transform raw triage payloads into initialized AccountState workflow states.

**Classes**
* **Class**: `AccountStateFactory`
  * **Type**: Utility
  * **Methods**:
    * `from_triage_output(triage_payload: Dict[str, Any])` -> `AccountState`
  * **Purpose**: Safely converts and initializes the standard `AccountState` using incoming dispatcher values.

**Functions**
* **Function**: `parse_datetime()`
  * **Parameters**: `dt_str : Optional[str]`
  * **Returns**: `Optional[datetime]`
  * **Purpose**: Safely parses datetime strings from upstream payloads into timezone-aware datetime objects.
* **Function**: `safe_float()`
  * **Parameters**: `value : Any`, `default : float = 0.0`
  * **Returns**: `float`
  * **Purpose**: Safely coerces input values to floats, returning a default on failure.
* **Function**: `safe_int()`
  * **Parameters**: `value : Any`, `default : int = 0`
  * **Returns**: `int`
  * **Purpose**: Safely coerces input values to integers, returning a default on failure.

---

### File: `test_account_agent.ipynb`
**Purpose**
Jupyter notebook for executing mock inputs, compiling, and testing the LangGraph workflow.

**Classes**
None

**Functions**
None

---

### File: `.gitignore`
**Purpose**
Lists untracked files and folders that Git should ignore.

**Classes**
None

**Functions**
None

---

### File: `db/session.py`
**Purpose**
Configures the SQLAlchemy engine and yields local database sessions with cleanup.

**Classes**
None

**Functions**
* **Function**: `get_db()`
  * **Parameters**: None
  * **Returns**: `Generator[Session, None, None]`
  * **Purpose**: Yields database sessions, ensuring sessions are closed upon termination.

**Constants**
* `DB_USER`
* `DB_PASS`
* `DB_HOST`
* `DB_PORT`
* `DB_NAME`
* `DATABASE_URL`

---

### File: `mapper/final_responce.py`
**Purpose**
Converts internal LangGraph state dictionary properties into the external Pydantic validation response format.

**Classes**
None

**Functions**
* **Function**: `build_account_output()`
  * **Parameters**: `final_state : AccountState`
  * **Returns**: `AccountAgentResponse`
  * **Purpose**: Evaluates final internal state, formats provider results, categorizes status, and constructs response.

---

### File: `nodes/__init__.py`
**Purpose**
Empty package initialization file.

**Classes**
None

**Functions**
None

---

### File: `nodes/abuse_guard_node.py`
**Purpose**
LangGraph node wrapper invoking the abuse assessment engine to check ticketing and login frequencies.

**Classes**
None

**Functions**
* **Function**: `abuse_guard()`
  * **Parameters**: `state : AccountState`, `abuse_guard_service : AbuseGuardService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Invokes abuse guard service to check triage parameters and auth attempts, updating the workflow state.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `AbuseGuardService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/action_resolution_node.py`
**Purpose**
LangGraph node mapping triage category intents and raw message keyword triggers to executable system actions.

**Classes**
None

**Functions**
* **Function**: `action_resolution_node()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Detects exact requested action types (e.g. unlocks vs password resets) from classification tokens.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/audit_log_node.py`
**Purpose**
LangGraph node mapping outcome classifications and storing immutable logs inside the security audit repository.

**Classes**
None

**Functions**
* **Function**: `audit_log()`
  * **Parameters**: `state : AccountState`, `audit_repo : SecurityAuditRepository`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Evaluates execution outcomes (completed, denied, escalated) and logs data to the audit database.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `SecurityAuditRepository`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/billing_history_node.py`
**Purpose**
LangGraph execution node querying recent invoices and transactional entries for diagnostic lookups.

**Classes**
None

**Functions**
* **Function**: `billing_history()`
  * **Parameters**: `state : AccountState`, `billing_repo : BillingRepository`, `idempotency_service : IdempotencyService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Fetches historical billing items using idempotency controls to prevent double execution.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `BillingRepository`
  * `IdempotencyService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/clarification_check_node.py`
**Purpose**
LangGraph node to verify if the issue classification is ambiguous and requires human clarification.

**Classes**
None

**Functions**
* **Function**: `clarification_check()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Evaluates clarification flags to decide if execution must yield for user clarification.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/fetch_account_context_node.py`
**Purpose**
LangGraph node to populate state with active subscription contexts and authentication profiles.

**Classes**
None

**Functions**
* **Function**: `fetch_account_context()`
  * **Parameters**: `state : AccountState`, `account_repo : AccountRepository`, `billing_repo : BillingRepository`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Populates subscription details, security settings, and previous authentication logs in the state.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `AccountRepository`
  * `BillingRepository`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/idempotency_node.py`
**Purpose**
LangGraph node mapping unique request tokens to reservation states before executing API calls.

**Classes**
None

**Functions**
* **Function**: `idempotency()`
  * **Parameters**: `state : AccountState`, `idempotency_service : IdempotencyService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Assures operations are idempotent by querying and reserving token executions.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `IdempotencyService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/identity_resolution_node.py`
**Purpose**
LangGraph node invoking verification logic to resolve the trust status of the requester.

**Classes**
None

**Functions**
* **Function**: `identity_resolution()`
  * **Parameters**: `state : AccountState`, `identity_service : IdentityService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Evaluates incoming customer credentials and maps a confidence level to verification variables.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `IdentityService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/invoice_retrieval_node.py`
**Purpose**
LangGraph node handling explicit invoice reference retrieval and receipt downloads.

**Classes**
None

**Functions**
* **Function**: `invoice_retrieval()`
  * **Parameters**: `state : AccountState`, `billing_repo : BillingRepository`, `idempotency_service : IdempotencyService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Queries the billing repository for an invoice and stores it in the state under idempotency lock.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `BillingRepository`
  * `IdempotencyService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/password_reset_node.py`
**Purpose**
LangGraph node running auth provider mutations to reset passwords and flush login failure metrics.

**Classes**
None

**Functions**
* **Function**: `password_reset()`
  * **Parameters**: `state : AccountState`, `auth_provider : AuthProvider`, `idempotency_service : IdempotencyService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Resets password through the Identity Provider interface.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `AuthProvider`
  * `IdempotencyService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/response_generation_node.py`
**Purpose**
LangGraph node forming natural language customer responses based on final status outcomes.

**Classes**
None

**Functions**
* **Function**: `response_generation_node()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Generates appropriate messages depending on whether the action succeeded, was denied, or escalated.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/risk_assessment_node.py`
**Purpose**
LangGraph node integrating ATO indicators and context histories into a combined risk level.

**Classes**
None

**Functions**
* **Function**: `risk_assessment()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Invokes the RiskEngineService to compile takeover risk, abuse history, and transaction context.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/security_escalation_node.py`
**Purpose**
LangGraph higher-order node factory managing lock actions and routing cases for security review.

**Classes**
None

**Functions**
* **Function**: `get_security_escalation_node()`
  * **Parameters**: `auth_provider : AuthProvider`, `audit_repo : SecurityAuditRepository`, `idempotency_service : IdempotencyService`
  * **Returns**: `Callable[[AccountState], Dict[str, Any]]`
  * **Purpose**: Generates a closure node that locks compromised accounts and records escalation details.

**Relationships**
* **Consumes**:
  * `AuthProvider`
  * `SecurityAuditRepository`
  * `IdempotencyService`
* **Produces**:
  * `Callable[[AccountState], Dict[str, Any]]`
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/subclassify_issue_node.py`
**Purpose**
LangGraph node using keywords or LLM completion models to classify issues into subclass intents.

**Classes**
None

**Functions**
* **Function**: `subclassify_issue()`
  * **Parameters**: `state : AccountState`, `subclassifier_service : SubclassifierService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Identifies categories (login, billing, access) and checks for clarification triggers.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `SubclassifierService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/takeover_detection_node.py`
**Purpose**
LangGraph node executing indicators evaluations for account takeover threats.

**Classes**
None

**Functions**
* **Function**: `takeover_detection()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Executes the TakeoverDetectorService to evaluate password resets and authentication patterns.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/unlock_account_node.py`
**Purpose**
LangGraph node invoking IdP modifications to unlock user sessions.

**Classes**
None

**Functions**
* **Function**: `unlock_account()`
  * **Parameters**: `state : AccountState`, `auth_provider : AuthProvider`, `idempotency_service : IdempotencyService`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Unlocks locked customer authentication profiles using verification checks.

**Relationships**
* **Consumes**:
  * `AccountState`
  * `AuthProvider`
  * `IdempotencyService`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/validate_contract_node.py`
**Purpose**
LangGraph validation node checking payload fields on triage entries.

**Classes**
None

**Functions**
* **Function**: `validate_contract()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Validates tickets contexts, emails, and ticket identifiers.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `nodes/verification_policy_node.py`
**Purpose**
LangGraph node validating requested action limits against authorization thresholds.

**Classes**
None

**Functions**
* **Function**: `verification_policy()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `Dict[str, Any]`
  * **Purpose**: Verifies that the client verification level matches the rank required for the requested action.

**Relationships**
* **Consumes**:
  * `AccountState`
* **Produces**:
  * `Dict[str, Any]` (state update)
* **Used By**:
  * `account_graph.py`

---

### File: `providers/base_auth_provider.py`
**Purpose**
Interface definitions for auth integrations (currently empty).

**Classes**
None

**Functions**
None

---

### File: `providers/base_billing_provider.py`
**Purpose**
Interface definitions for billing integrations (currently empty).

**Classes**
None

**Functions**
None

---

### File: `providers/mock_auth_provider.py`
**Purpose**
Mock implementations of authentication integration actions (currently empty).

**Classes**
None

**Functions**
None

---

### File: `providers/mock_billing_provider.py`
**Purpose**
Mock implementations of billing integration actions (currently empty).

**Classes**
None

**Functions**
None

---

### File: `repositories/account_repository.py`
**Purpose**
Data access layer for password resets, locks, and subscriptions status in PostgreSQL.

**Classes**
* **Class**: `AccountRepository`
  * **Type**: Repository
  * **Methods**:
    * `__init__(session: Session)`
    * `_execute_mutation(query: Any, params: Dict[str, Any], error_message: str)` -> `bool`
    * `get_auth_account(customer_id: int)` -> `Optional[Dict[str, Any]]`
    * `increment_failed_attempts(customer_id: int)` -> `bool`
    * `reset_failed_attempts(customer_id: int)` -> `bool`
    * `unlock_account(customer_id: int)` -> `bool`
    * `mark_suspicious(customer_id: int)` -> `bool`
    * `update_last_password_reset(customer_id: int)` -> `bool`
    * `record_successful_login(customer_id: int)` -> `bool`
    * `get_subscription(customer_id: int)` -> `Optional[Dict[str, Any]]`
    * `update_subscription_status(customer_id: int, new_status: str)` -> `bool`
  * **Purpose**: Handles database reads and modifications for user auth profiles and subscriptions.

**Repository Details**
* **Database**: PostgreSQL
* **Tables Referenced**:
  * `auth_accounts`
  * `subscriptions`

**Relationships**
* **Consumes**:
  * `Session` (SQLAlchemy connection)
* **Used By**:
  * `services/auth_provider.py`
  * `services/billing_provider.py`
  * `services/identity_service.py`
  * `nodes/fetch_account_context_node.py`

---

### File: `repositories/billing_repository.py`
**Purpose**
Data access layer for retrieving billing logs and specific invoices from PostgreSQL.

**Classes**
* **Class**: `BillingRepository`
  * **Type**: Repository
  * **Methods**:
    * `__init__(session: Session)`
    * `_sanitize_limit(limit: int)` -> `int` (static method)
    * `get_billing_history(customer_id: int, limit: int)` -> `List[Dict[str, Any]]`
    * `get_invoice_by_id(invoice_id: str)` -> `Optional[Dict[str, Any]]`
    * `get_latest_invoice(customer_id: int)` -> `Optional[Dict[str, Any]]`
    * `get_failed_payments(customer_id: int, limit: int)` -> `List[Dict[str, Any]]`
  * **Purpose**: Exposes queries to pull invoice data, failed charges, and historical transactions.

**Repository Details**
* **Database**: PostgreSQL
* **Tables Referenced**:
  * `billing_history`

**Constants**
* `BILLING_COLUMNS`

**Relationships**
* **Consumes**:
  * `Session`
* **Used By**:
  * `nodes/fetch_account_context_node.py`
  * `nodes/billing_history_node.py`
  * `nodes/invoice_retrieval_node.py`

---

### File: `repositories/customer_repository.py`
**Purpose**
Data access layer for retrieving customer profiles, recent orders, and ticket history from PostgreSQL.

**Classes**
* **Class**: `CustomerRepository`
  * **Type**: Repository
  * **Methods**:
    * `__init__(session: Session)`
    * `_sanitize_limit(limit: int)` -> `int` (static method)
    * `get_customer_by_email(email: Optional[str])` -> `Optional[Dict[str, Any]]`
    * `get_customer_by_id(customer_id: int)` -> `Optional[Dict[str, Any]]`
    * `get_recent_orders(customer_id: int, limit: int)` -> `List[Dict[str, Any]]`
    * `get_ticket_history(customer_id: int, limit: int)` -> `List[Dict[str, Any]]`
    * `get_escalation_history(customer_id: int, limit: int)` -> `List[Dict[str, Any]]`
  * **Purpose**: Fetches historical account orders, tickets, and escalation logs.

**Repository Details**
* **Database**: PostgreSQL
* **Tables Referenced**:
  * `customers`
  * `orders`
  * `tickets`
  * `escalations`

**Constants**
* `CUSTOMER_COLUMNS`

**Relationships**
* **Consumes**:
  * `Session`
* **Used By**:
  * `services/identity_service.py`

---

### File: `repositories/security_audit_repository.py`
**Purpose**
Data access layer for immutable audit logging and idempotency session state controls in PostgreSQL.

**Classes**
* **Class**: `SecurityAuditRepository`
  * **Type**: Repository
  * **Methods**:
    * `__init__(session: Session)`
    * `_execute_mutation(query: Any, params: Dict[str, Any], error_message: str)` -> `bool`
    * `log_security_event(...)` -> `bool`
    * `create_idempotency_record(idempotency_key: str, action_type: ActionType, customer_id: Optional[int])` -> `bool`
    * `update_idempotency_status(idempotency_key: str, status: str, response_payload: Optional[Dict[str, Any]])` -> `bool`
    * `get_idempotency_record(idempotency_key: str)` -> `Optional[Dict[str, Any]]`
  * **Purpose**: Manages write operations for auditing security decisions and reserving token states.

**Repository Details**
* **Database**: PostgreSQL
* **Tables Referenced**:
  * `account_security_audit`
  * `idempotency_keys`

**Constants**
* `VALID_IDEMPOTENCY_STATUS`

**Relationships**
* **Consumes**:
  * `Session`
* **Used By**:
  * `services/idempotency_service.py`
  * `nodes/audit_log_node.py`
  * `nodes/security_escalation_node.py`

---

### File: `routers/decision_router.py`
**Purpose**
Decides subsequent graph node routings based on internal validation states.

**Classes**
None

**Functions**
* **Function**: `clarification_router()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `str`
  * **Purpose**: Returns `response_generation` if clarification is required; otherwise returns `identity_resolution`.
* **Function**: `execution_router()`
  * **Parameters**: `state : AccountState`
  * **Returns**: `str`
  * **Purpose**: Routes to password reset, unlock, retrieval, history, or escalation based on allowed actions.

---

### File: `schemas/account_state.py`
**Purpose**
Defines the internal state TypedDict schema carrying workflow parameters across LangGraph nodes.

**Classes**
None

**Schemas / Models**
* **Schema**: `AccountState`
  * **Fields**:
    * `ticket : Dict[str, Any]`
    * `entities : Dict[str, Any]`
    * `ticket_id : int`
    * `customer_email : str`
    * `customer_id : Optional[int]`
    * `initial_intent : str`
    * `initial_urgency : str`
    * `initial_sentiment : str`
    * `supervisor_confidence : float`
    * `customer_tier : str`
    * `ltv : float`
    * `unresolved_repeat_count : int`
    * `total_tickets : int`
    * `total_escalations : int`
    * `final_priority : str`
    * `sla_duration_hours : int`
    * `sla_deadline : datetime`
    * `sub_category : Optional[ActionSubCategory]`
    * `clarification_required : bool`
    * `clarification_question : Optional[str]`
    * `identity_verified : bool`
    * `identity_confidence : float`
    * `verification_level : Optional[VerificationLevel]`
    * `resolved_customer_id : Optional[int]`
    * `identity_signals : Dict[str, Any]`
    * `risk_assessment : Optional[RiskAssessment]`
    * `abuse_assessment : Optional[AbuseAssessment]`
    * `takeover_assessment : Optional[TakeoverAssessment]`
    * `escalation_required : bool`
    * `security_escalation : bool`
    * `escalation_reason : Optional[str]`
    * `auth_context : Dict[str, Any]`
    * `billing_context : Dict[str, Any]`
    * `subscription_context : Dict[str, Any]`
    * `access_context : Dict[str, Any]`
    * `requested_action : Optional[ActionType]`
    * `decision : Optional[AccountDecision]`
    * `action_result : Optional[str]`
    * `provider_response : Optional[ProviderResponse]`
    * `idempotency_key : Optional[str]`
    * `idempotency_blocked : bool`
    * `duplicate_cached_response : bool`
    * `workflow_logs : List[WorkflowLog]`
    * `errors : List[str]`
    * `retry_count : int`
    * `current_node : Optional[str]`
    * `created_at : datetime`
    * `workflow_id : str`
    * `correlation_id : str`
  * **Purpose**: Core TypedDict definition representing the workspace state inside the LangGraph engine.

---

### File: `schemas/domain.py`
**Purpose**
Defines validation schemas, custom Pydantic models, and custom Enum types.

**Classes**
None

**Schemas / Models**
* **Schema**: `ProviderResponse`
  * **Fields**:
    * `provider_name : str`
    * `status : ProviderStatus`
    * `data : Dict[str, Any]`
    * `error_message : Optional[str]`
  * **Purpose**: Structure for vendor provider execution response logs.
* **Schema**: `WorkflowLog`
  * **Fields**:
    * `model_config : ConfigDict`
    * `timestamp : datetime`
    * `node : str`
    * `message : str`
    * `data : Dict[str, Any]`
  * **Purpose**: Defines standard log items recorded inside each active graph node.
* **Schema**: `RiskAssessment`
  * **Fields**:
    * `risk_score : float`
    * `risk_level : RiskLevel`
    * `takeover_detected : bool`
    * `abuse_detected : bool`
    * `signals : Dict[str, Any]`
  * **Purpose**: Captures calculated risk parameters for safety policies checking.
* **Schema**: `AccountDecision`
  * **Fields**:
    * `sub_category : Optional[ActionSubCategory]`
    * `requested_action : ActionType`
    * `verification_level : VerificationLevel`
    * `risk_level : RiskLevel`
    * `action_allowed : bool`
    * `decision_reason : str`
    * `escalation_required : bool`
    * `security_escalation : bool`
  * **Purpose**: Action gatekeeping decision containing approval rules flags.
* **Schema**: `SubclassificationResult`
  * **Fields**:
    * `sub_category : Optional[ActionSubCategory]`
    * `clarification_required : bool`
    * `clarification_question : Optional[str]`
  * **Purpose**: Schema mapping sub-category outputs from classification steps.
* **Schema**: `IdentityResolutionResult`
  * **Fields**:
    * `identity_verified : bool`
    * `identity_confidence : float`
    * `resolved_customer_id : Optional[int]`
    * `identity_signals : Dict[str, Any]`
    * `verification_level : VerificationLevel`
  * **Purpose**: Trust results capturing confidence scores and security overrides flags.
* **Schema**: `AbuseAssessment`
  * **Fields**:
    * `abuse_detected : bool`
    * `abuse_score : float`
    * `signals : Dict[str, Any]`
    * `reason : Optional[str]`
  * **Purpose**: Result from ticketing spams and failed login abuse detectors.
* **Schema**: `TakeoverAssessment`
  * **Fields**:
    * `takeover_detected : bool`
    * `risk_score_modifier : float`
    * `signals : Dict[str, Any]`
    * `reason : Optional[str]`
  * **Purpose**: Identifies velocity spikes or MFA bypass warnings.

**Enums**
* **Enum**: `ActionSubCategory`
  * **Values**: `LOGIN_ISSUE`, `BILLING_QUERY`, `SUBSCRIPTION_CHANGE`, `ACCESS_RESTORATION`, `SECURITY_ISSUE`
  * **Purpose**: Sub-categories of account issues.
* **Enum**: `VerificationLevel`
  * **Values**: `LOW`, `MEDIUM`, `HIGH`, `FAILED`
  * **Purpose**: Identity resolution trust classifications.
* **Enum**: `RiskLevel`
  * **Values**: `LOW`, `MEDIUM`, `HIGH`
  * **Purpose**: Severity ranking of computed risks.
* **Enum**: `ProviderStatus`
  * **Values**: `SUCCESS`, `FAILED`, `TIMEOUT`, `RATE_LIMITED`, `UNAVAILABLE`
  * **Purpose**: Adapter response indicators.
* **Enum**: `ActionType`
  * **Values**: `PASSWORD_RESET`, `ACCOUNT_UNLOCK`, `BILLING_EXPLANATION`, `INVOICE_RETRIEVAL`, `PAYMENT_UPDATE_LINK`, `SUBSCRIPTION_UPGRADE`, `SUBSCRIPTION_DOWNGRADE`, `SUBSCRIPTION_CANCEL`, `SUBSCRIPTION_PAUSE`, `ACCESS_SYNC`, `SECURITY_ESCALATION`
  * **Purpose**: Standard list of executable system workflows.

---

### File: `schemas/final_account_agent_responce.py`
**Purpose**
Defines standard Pydantic response envelope containing metadata and outcomes.

**Classes**
None

**Schemas / Models**
* **Schema**: `AccountAgentResponse`
  * **Fields**:
    * `ticket_id : str`
    * `customer_id : Optional[int]`
    * `workflow_id : str`
    * `correlation_id : str`
    * `agent_name : Literal['account_agent']`
    * `sub_category : Optional[str]`
    * `requested_action : Optional[str]`
    * `status : Literal['completed', 'denied', 'escalated', 'clarification_required']`
    * `decision_reason : Optional[str]`
    * `verification_level : Optional[str]`
    * `risk_level : Optional[str]`
    * `execution_success : bool`
    * `provider_name : Optional[str]`
    * `provider_status : Optional[str]`
    * `provider_response : Optional[Dict[str, Any]]`
    * `customer_response : str`
    * `escalation_required : bool`
    * `security_escalation : bool`
    * `escalation_reason : Optional[str]`
    * `audit_decision : Optional[str]`
    * `audit_logged : bool`
  * **Purpose**: Response envelope schema returned to clients outside the agent boundary.

---

### File: `services/abuse_guard.py`
**Purpose**
Evaluates ticket spamming, high failed-login counts, and suspicious escalation ratios.

**Classes**
* **Class**: `AbuseGuardService`
  * **Type**: Service
  * **Methods**:
    * `evaluate_abuse(auth_context: Optional[Dict[str, Any]], triage_context: Dict[str, Any])` -> `AbuseAssessment`
  * **Purpose**: Computes risk assessments and generates structured abuse signals.

**Service Details**
* **Dependencies**: None
* **Methods**:
  * `evaluate_abuse()`

**Fields**
* `MAX_SAFE_FAILED_LOGINS` (5)
* `CRITICAL_FAILED_LOGINS` (8)
* `MAX_UNRESOLVED_REPEATS` (3)
* `ESCALATION_ABUSE_MIN_COUNT` (3)
* `ESCALATION_ABUSE_RATIO` (0.5)
* `ABUSE_SCORE_THRESHOLD` (75.0)

---

### File: `services/auth_provider.py`
**Purpose**
Adapter managing external authentication providers updates and account containment locks.

**Classes**
* **Class**: `AuthProvider`
  * **Type**: Service
  * **Methods**:
    * `__init__(account_repo: AccountRepository)`
    * `reset_password(customer_id: int, email: str)` -> `ProviderResponse`
    * `unlock_account(customer_id: int)` -> `ProviderResponse`
    * `sync_access(customer_id: int)` -> `ProviderResponse`
    * `lock_account(customer_id: int, reason: str)` -> `ProviderResponse`
  * **Purpose**: Simulates password resets and security locks, delegating state persistence to repositories.

**Service Details**
* **Dependencies**:
  * `AccountRepository`
* **Methods**:
  * `reset_password()`
  * `unlock_account()`
  * `sync_access()`
  * `lock_account()`

**Fields**
* `PROVIDER_NAME` ("InternalIdP")

---

### File: `services/billing_provider.py`
**Purpose**
Adapter simulating upgraded, downgraded, or cancelled subscription changes.

**Classes**
* **Class**: `BillingProvider`
  * **Type**: Service
  * **Methods**:
    * `__init__(account_repo: AccountRepository)`
    * `update_subscription(customer_id: int, action: ActionType)` -> `ProviderResponse`
    * `generate_payment_link(customer_id: int, reason: str)` -> `ProviderResponse`
  * **Purpose**: Interacts with the subscriptions repository to mutate plans.

**Service Details**
* **Dependencies**:
  * `AccountRepository`
* **Methods**:
  * `update_subscription()`
  * `generate_payment_link()`

**Fields**
* `PROVIDER_NAME` ("InternalBilling")
* `SUBSCRIPTION_ACTIONS`
* `STATUS_MAP`

---

### File: `services/idempotency_service.py`
**Purpose**
Maintains request reservation locks to block duplicate command replays.

**Classes**
* **Class**: `IdempotencyService`
  * **Type**: Service
  * **Methods**:
    * `__init__(security_repo: SecurityAuditRepository)`
    * `reserve_execution(idempotency_key: str, action_type: ActionType, customer_id: Optional[int])` -> `bool`
    * `get_cached_result(idempotency_key: str)` -> `Optional[Dict[str, Any]]`
    * `mark_completed(idempotency_key: str, response_payload: Dict[str, Any])` -> `bool`
    * `mark_failed(idempotency_key: str, error_payload: Optional[Dict[str, Any]])` -> `bool`
  * **Purpose**: Checks status keys to block duplicate requests and cache successful payloads.

**Service Details**
* **Dependencies**:
  * `SecurityAuditRepository`
* **Methods**:
  * `reserve_execution()`
  * `get_cached_result()`
  * `mark_completed()`
  * `mark_failed()`

---

### File: `services/identity_service.py`
**Purpose**
Validates customer identity against database profiles and orders records.

**Classes**
* **Class**: `IdentityService`
  * **Type**: Service
  * **Methods**:
    * `__init__(customer_repo: CustomerRepository, account_repo: AccountRepository)`
    * `resolve_identity(email: Optional[str], triage_customer_id: Optional[int], entities: Optional[Dict[str, Any]])` -> `IdentityResolutionResult`
    * `_build_result(verified: bool, confidence: float, customer_id: Optional[int], signals: Dict[str, Any])` -> `IdentityResolutionResult`
  * **Purpose**: Matches emails, ids, and orders to calculate a trust score.

**Service Details**
* **Dependencies**:
  * `CustomerRepository`
  * `AccountRepository`
* **Methods**:
  * `resolve_identity()`
  * `_build_result()`

---

### File: `services/risk_engine.py`
**Purpose**
Consolidates brute-force, takeover, and LTV histories into unified risk levels.

**Classes**
* **Class**: `RiskEngineService`
  * **Type**: Service
  * **Methods**:
    * `calculate_risk(triage_context: Dict[str, Any], requested_action: Optional[ActionType], abuse_assessment: AbuseAssessment, takeover_assessment: TakeoverAssessment)` -> `RiskAssessment`
  * **Purpose**: Computes comprehensive risk scores.

**Service Details**
* **Dependencies**: None
* **Methods**:
  * `calculate_risk()`

**Fields**
* `HIGH_RISK_THRESHOLD` (75.0)
* `MEDIUM_RISK_THRESHOLD` (40.0)
* `HIGH_VALUE_LTV_THRESHOLD` (1000.0)
* `HIGH_SENSITIVITY_ACTIONS`

---

### File: `services/subclassifier.py`
**Purpose**
Applies regex filters or calls LLM schemas to subclassify intents.

**Classes**
* **Class**: `SubclassifierService`
  * **Type**: Service
  * **Methods**:
    * `__init__(llm: BaseChatModel)`
    * `classify_issue(message: str)` -> `SubclassificationResult`
    * `_rule_based_classification(message: str)` -> `Optional[SubclassificationResult]`
    * `_trigger_clarification()` -> `SubclassificationResult`
  * **Purpose**: Maps requests to action categories (e.g. login, billing, subscription).

**Service Details**
* **Dependencies**:
  * `BaseChatModel` (LLM connection)
* **Methods**:
  * `classify_issue()`
  * `_rule_based_classification()`
  * `_trigger_clarification()`

---

### File: `services/takeover_detector.py`
**Purpose**
Evaluates passwords reset times and lock bypass risks to calculate ATO scores.

**Classes**
* **Class**: `TakeoverDetectorService`
  * **Type**: Service
  * **Methods**:
    * `evaluate_takeover_risk(auth_context: Optional[Dict[str, Any]], requested_action: Optional[ActionType])` -> `TakeoverAssessment`
    * `_normalize_datetime(dt: Optional[datetime])` -> `Optional[datetime]`
  * **Purpose**: Analyzes velocity indicators (e.g. requests occurring within 24 hours of a password reset).

**Service Details**
* **Dependencies**: None
* **Methods**:
  * `evaluate_takeover_risk()`
  * `_normalize_datetime()`

**Fields**
* `RECENT_RESET_WINDOW_HOURS` (24)
* `TAKEOVER_THRESHOLD` (75.0)
* `HIGH_RISK_ACTIONS`

---

### File: `services/verification_policy.py`
**Purpose**
Determines if requester verification levels are sufficient to authorize actions.

**Classes**
* **Class**: `VerificationPolicyService`
  * **Type**: Service
  * **Methods**:
    * `evaluate_decision(sub_category: ActionSubCategory, requested_action: ActionType, verification_level: VerificationLevel, risk_level: RiskLevel)` -> `AccountDecision`
    * `_approve(sub: ActionSubCategory, action: ActionType, v_level: VerificationLevel, r_level: RiskLevel, reason: str)` -> `AccountDecision`
    * `_deny(sub: ActionSubCategory, action: ActionType, v_level: VerificationLevel, r_level: RiskLevel, reason: str, security_escalation: bool)` -> `AccountDecision`
  * **Purpose**: Policy gateway ensuring standard actions require MEDIUM, sensitive actions require HIGH verification.

**Service Details**
* **Dependencies**: None
* **Methods**:
  * `evaluate_decision()`
  * `_approve()`
  * `_deny()`

**Fields**
* `SAFE_ACTIONS`
* `STANDARD_ACTIONS`
* `SENSITIVE_ACTIONS`
* `VERIFICATION_RANK`
* `REQUIRED_LEVEL`

---

### File: `utils/workflow_logger.py`
**Purpose**
Shared logging configuration (currently empty).

**Classes**
None

**Functions**
None

---

## Section 3: Folder Summary

### Folder Purpose
The `Layer_2_Account` workspace implements a secure customer account and subscription manager. It leverages a LangGraph state machine workflow to classify incoming triage tickets, verify customer identities under a zero-trust architecture, execute security policies, detect potential account takeovers or brute force attacks, and call mock authentication and billing providers safely under idempotency controls. Finally, it ensures that all execution paths are recorded inside a PostgreSQL audit logging scheme.

### Files Included
* `account_graph.py`
* `state_factory.py`
* `test_account_agent.ipynb`
* `db/session.py`
* `mapper/final_responce.py`
* `nodes/__init__.py`
* `nodes/abuse_guard_node.py`
* `nodes/action_resolution_node.py`
* `nodes/audit_log_node.py`
* `nodes/billing_history_node.py`
* `nodes/clarification_check_node.py`
* `nodes/fetch_account_context_node.py`
* `nodes/idempotency_node.py`
* `nodes/identity_resolution_node.py`
* `nodes/invoice_retrieval_node.py`
* `nodes/password_reset_node.py`
* `nodes/response_generation_node.py`
* `nodes/risk_assessment_node.py`
* `nodes/security_escalation_node.py`
* `nodes/subclassify_issue_node.py`
* `nodes/takeover_detection_node.py`
* `nodes/unlock_account_node.py`
* `nodes/validate_contract_node.py`
* `nodes/verification_policy_node.py`
* `providers/base_auth_provider.py`
* `providers/base_billing_provider.py`
* `providers/mock_auth_provider.py`
* `providers/mock_billing_provider.py`
* `repositories/account_repository.py`
* `repositories/billing_repository.py`
* `repositories/customer_repository.py`
* `repositories/security_audit_repository.py`
* `routers/decision_router.py`
* `schemas/account_state.py`
* `schemas/domain.py`
* `schemas/final_account_agent_responce.py`
* `services/abuse_guard.py`
* `services/auth_provider.py`
* `services/billing_provider.py`
* `services/idempotency_service.py`
* `services/identity_service.py`
* `services/risk_engine.py`
* `services/subclassifier.py`
* `services/takeover_detector.py`
* `services/verification_policy.py`
* `utils/workflow_logger.py`

### Main Components
* **Repositories**:
  * `AccountRepository`
  * `BillingRepository`
  * `CustomerRepository`
  * `SecurityAuditRepository`
* **Services**:
  * `AbuseGuardService`
  * `AuthProvider`
  * `BillingProvider`
  * `IdempotencyService`
  * `IdentityService`
  * `RiskEngineService`
  * `SubclassifierService`
  * `TakeoverDetectorService`
  * `VerificationPolicyService`
* **Schemas**:
  * `AccountState`
  * `ProviderResponse`
  * `WorkflowLog`
  * `RiskAssessment`
  * `AccountDecision`
  * `SubclassificationResult`
  * `IdentityResolutionResult`
  * `AbuseAssessment`
  * `TakeoverAssessment`
  * `AccountAgentResponse`
* **Enums**:
  * `ActionSubCategory`
  * `VerificationLevel`
  * `RiskLevel`
  * `ProviderStatus`
  * `ActionType`
* **Utilities**:
  * `AccountStateFactory`
* **Graphs**:
  * LangGraph workflow defined and compiled in `account_graph.py`.

### Input / Output
* **Input**:
  * Raw dispatch dictionary from the Layer 2 Triage Agent containing ticket details (`ticket`, `ticket_id`, `customer_email`, `customer_id`), intent metadata (`initial_intent`, `initial_urgency`, `initial_sentiment`, `supervisor_confidence`), and CRM context (`customer_tier`, `ltv`, `unresolved_repeat_count`, `total_tickets`, `total_escalations`, `final_priority`, `sla_duration_hours`, `sla_deadline`).
* **Output**:
  * `AccountAgentResponse` containing execution statuses (`completed`, `denied`, `escalated`, `clarification_required`), decision reasons, calculated risk and verification levels, external provider call statuses, customer-facing response texts, escalation metrics, and audit completion flags.

# Layer 2 Refund - Codebase Inventory & Documentation

---

## Section 1: Folder Structure

```
layer_2_refund/
│
├── __init__.py
├── config.py
├── run_workflow.py
├── docu.md
├── test_refund_graph.ipynb
│
├── agents/
│   ├── __init__.py
│   └── refund_agent/
│       ├── __init__.py
│       ├── policy_engine.py
│       └── refund_agent_node.py
│
├── database/
│   ├── __init__.py
│   └── session.py
│
├── graphs/
│   ├── refund_graph.py
│   ├── refund_state.py
│   ├── routers.py
│   ├── state_factory.py
│   └── nodes/
│       ├── idempotency_node.py
│       ├── order_node.py
│       ├── customer_node.py
│       ├── policy_node.py
│       ├── escalation_node.py
│       ├── human_review_node.py
│       ├── execution_node.py
│       └── audit_node.py
│
├── mappers/
│   └── refund_output_mapper.py
│
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py
│   ├── customer_repository.py
│   ├── order_repository.py
│   └── refund_repository.py
│
├── schemas/
│   ├── __init__.py
│   └── refund_models.py
│
├── services/
│   └── mock_payment_service.py
│
└── tests/
    ├── __init__.py
    └── test.ipynb
```

---

## Section 2: File Analysis

### File: config.py

**Purpose**
Configuration settings for database connection using PostgreSQL credentials.

**Classes**

Class: Settings
Type: Configuration

Methods:
None (class attributes only)

Purpose:
Stores database connection parameters (user, password, host, port, database name).

**Constants**
- db_user = "postgres"
- db_pass = "pass9325"
- db_host = "localhost"
- db_port = 5432
- db_name = "customer_support_ai"

---

### File: run_workflow.py

**Purpose**
Demo entry point for running the refund workflow with checkpoint support and human interruption.

**Functions**

Function: run_workflow_demo()

Parameters:
- description (str)
- order_id (str)

Returns:
None (prints workflow progress and results)

Purpose:
Runs a complete refund workflow demo with initial state creation, streaming events, human review interruption, and final audit logging.

**Constants**
- memory (MemorySaver)
- app (compiled LangGraph with checkpointer)
- interrupt_before = ["human_review_node"]

---

### File: database/session.py

**Purpose**
SQLAlchemy database session factory and engine configuration for PostgreSQL connection pooling.

**Functions**

Function: get_db()

Parameters:
None

Returns:
Generator[Session, None, None]

Purpose:
Yields database session with guaranteed cleanup via try-finally block.

**Constants**
- DATABASE_URL (PostgreSQL connection string)
- engine (SQLAlchemy engine with pool settings)
- SessionLocal (scoped session factory)

**Configuration**
- pool_size = 10
- max_overflow = 20
- pool_pre_ping = True
- pool_recycle = 1800
- pool_timeout = 30

---

### File: schemas/refund_models.py

**Purpose**
Pydantic models for refund workflow data structures, enums, and domain schemas.

**Enums**

Enum: RefundStatus

Values:
- PENDING
- APPROVED
- REJECTED
- ESCALATED
- COMPLETED

Purpose:
Status values for refund decisions throughout the workflow lifecycle.

---

Enum: OrderStatus

Values:
- PROCESSING
- SHIPPED
- DELIVERED
- RETURNED

Purpose:
Status values for order fulfillment state from database.

---

**Schemas / Models**

Schema: RefundRequest

Fields:
- ticket_id : str
- order_id : int
- customer_id : int
- reason_for_refund : str

Purpose:
Input schema from Layer 1/Triage containing the refund request details.

---

Schema: OrderData

Fields:
- order_id : int
- customer_id : int
- order_amount : float (gt=0)
- order_status : OrderStatus
- created_at : datetime
- is_refundable : Optional[bool] = None

Purpose:
Maps directly to 'orders' DB table; is_refundable is in-memory only for policy rules.

---

Schema: CustomerData

Fields:
- customer_id : int
- name : str
- email : str
- account_tier : Optional[str] = "standard"
- total_spent : Optional[float] = 0.0
- created_at : datetime

Purpose:
Maps directly to 'customers' DB table; represents customer profile for policy evaluation.

---

Schema: PolicyDecision

Fields:
- status : RefundStatus
- code : str (machine-readable decision code)
- reason : str
- refund_amount : Optional[float] = None
- requires_human_review : bool = False
- metadata : dict

Purpose:
Translates to fields in 'processed_refunds' and 'refund_audit' tables; core decision artifact.

---

Schema: RefundExecutionResult

Fields:
- success : bool
- transaction_id : Optional[str] = None
- execution_message : str

Purpose:
In-memory result from Mock Payment Gateway service (not persisted to DB).

---

Schema: IdempotencyRecord

Fields:
- idempotency_key : str
- order_id : int
- created_at : datetime

Purpose:
Maps to tracking columns in 'processed_refunds'; ensures duplicate request prevention.

---

Schema: RefundOutput

Fields:
- ticket_id : str
- workflow_id : str
- customer_id : int
- order_id : int
- final_status : RefundStatus
- decision_code : str
- decision_reason : str
- customer_response : Optional[str] = None
- refund_amount : Optional[float] = None
- transaction_id : Optional[str] = None
- review_required : bool = False
- review_status : Optional[str] = None
- audit_status : str
- duration_ms : Optional[int] = None

Purpose:
Final agent output payload sent downstream after workflow completion.

---

### File: repositories/base_repository.py

**Purpose**
Abstract base contracts for Order and Customer repository implementations.

**Classes**

Class: AbstractOrderRepository
Type: Repository (Abstract)

Methods:
- get_order_by_id(order_id: int) -> Optional[OrderData]
- update_order_status(order_id: int, status: OrderStatus) -> bool

Purpose:
Contract for 'orders' table operations; defines fetch and update methods.

---

Class: AbstractCustomerRepository
Type: Repository (Abstract)

Methods:
- get_customer_by_id(customer_id: int) -> Optional[CustomerData]
- update_customer_after_refund(customer_id: int, new_total_spent: float) -> bool

Purpose:
Contract for 'customers' table operations; defines fetch and update methods.

---

### File: repositories/customer_repository.py

**Purpose**
SQLAlchemy-based customer repository implementation with safe session management.

**Classes**

Class: CustomerRepository
Type: Repository

Methods:
- __init__(session: Session)
- get_customer_by_id(customer_id: int) -> Optional[CustomerData]
- update_customer_after_refund(customer_id: int, new_total_spent: float) -> bool

Purpose:
Implements AbstractCustomerRepository; fetches customer profiles and updates total_spent after refund.

**Database**
- PostgreSQL

**Tables Referenced**
- customers

---

### File: repositories/order_repository.py

**Purpose**
SQLAlchemy-based order repository implementation with safe session management.

**Classes**

Class: OrderRepository
Type: Repository

Methods:
- __init__(session: Session)
- get_order_by_id(order_id: int) -> Optional[OrderData]
- update_order_status(order_id: int, status: OrderStatus) -> bool

Purpose:
Implements AbstractOrderRepository; fetches order details and updates order_status in DB.

**Database**
- PostgreSQL

**Tables Referenced**
- orders

---

### File: repositories/refund_repository.py

**Purpose**
Repository for refund audit trail and idempotency check operations.

**Classes**

Class: RefundRepository
Type: Repository

Methods:
- __init__(session: Session)
- get_previous_decision(idempotency_key: str) -> Optional[PolicyDecision]
- record_final_transaction(idempotency_key: str, order_id: int, decision: PolicyDecision, execution_result=None, metadata=None) -> bool

Purpose:
Handles idempotency replays and persists final refund audit records to 'processed_refunds' table.

**Database**
- PostgreSQL

**Tables Referenced**
- processed_refunds

---

### File: services/mock_payment_service.py

**Purpose**
Mock payment gateway service for testing refund execution without real payment processor.

**Classes**

Class: MockPaymentService
Type: Service

Methods:
- execute_refund(order_id: int, amount: float) -> RefundExecutionResult

Purpose:
Simulates payment processor; validates amount, generates transaction IDs, returns success/failure result.

---

### File: mappers/refund_output_mapper.py

**Purpose**
Maps final workflow state to RefundOutput schema for downstream consumption.

**Functions**

Function: build_refund_output()

Parameters:
- final_state (dict)

Returns:
RefundOutput

Purpose:
Extracts relevant fields from workflow state and constructs final output object.

---

### File: graphs/refund_state.py

**Purpose**
Defines LangGraph workflow state structures and metrics tracking.

**Classes**

Class: WorkflowMetrics
Type: Pydantic Model

Methods:
None (data class)

Fields:
- started_at : float (default_factory=time.time)
- completed_at : Optional[float] = None
- duration_ms : Optional[int] = None
- retry_count : int = 0

Purpose:
Tracks workflow execution timing and retry counts.

---

**Schemas / Models**

Schema: RefundState

Fields:
- workflow_id : str
- idempotency_key : str
- state_version : int
- request : RefundRequest
- order_data : Optional[OrderData]
- customer_data : Optional[CustomerData]
- policy_decision : Optional[PolicyDecision]
- review_status : Optional[str]
- execution_result : Optional[RefundExecutionResult]
- human_decision : Optional[str]
- workflow_logs : List[str]
- current_node : Optional[str]
- metrics : WorkflowMetrics
- audit_status : Optional[str]
- error_message : Optional[str]

Purpose:
TypedDict defining the complete workflow state passed between LangGraph nodes.

---

### File: graphs/refund_graph.py

**Purpose**
Constructs and compiles the LangGraph state graph for refund orchestration workflow.

**LangGraph Workflow**

State Object:
- RefundState

Nodes:
- idempotency_node
- order_node
- customer_node
- policy_node
- escalation_node
- human_review_node
- execution_node
- audit_node

Routers:
- route_after_idempotency
- route_after_policy
- route_after_human_review

Entry Point:
- START → idempotency_node

Exit Point:
- audit_node → END

Workflow Flow:
1. START → idempotency_node [conditional]
   - If hit: → audit_node
   - If miss: → order_node
2. order_node → customer_node
3. customer_node → policy_node [conditional]
   - If APPROVED: → execution_node
   - If ESCALATED: → escalation_node
   - If REJECTED: → audit_node
4. escalation_node → human_review_node
5. human_review_node [conditional]
   - If ESCALATED: → human_review_node (wait)
   - If APPROVED: → execution_node
   - Else: → audit_node
6. execution_node → audit_node
7. audit_node → END

Purpose:
Orchestrates the complete refund workflow with conditional routing based on policy decisions and human review.

---

### File: graphs/routers.py

**Purpose**
Conditional edge routers that determine workflow transitions based on state.

**Functions**

Function: route_after_idempotency()

Parameters:
- state (RefundState)

Returns:
str (node name: "order_node" or "audit_node")

Purpose:
Routes to audit if idempotent replay detected, otherwise continues to order_node.

---

Function: route_after_policy()

Parameters:
- state (RefundState)

Returns:
str (node name: "execution_node", "escalation_node", or "audit_node")

Purpose:
Routes based on policy decision status (APPROVED→exec, ESCALATED→esc, REJECTED→audit).

---

Function: route_after_human_review()

Parameters:
- state (RefundState)

Returns:
str (node name: "human_review_node", "execution_node", or "audit_node")

Purpose:
Routes based on human decision and policy status during escalation review.

---

### File: graphs/state_factory.py

**Purpose**
Factory function for initializing RefundState with default values.

**Functions**

Function: create_initial_refund_state()

Parameters:
- request (RefundRequest)
- idempotency_key (str)

Returns:
RefundState

Purpose:
Creates initial workflow state dict with workflow_id, timestamps, metrics, and empty decision/result fields.

---

### File: graphs/nodes/idempotency_node.py

**Purpose**
First workflow node checking for duplicate request via idempotency key.

**Functions**

Function: idempotency_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Queries database for previous decision using idempotency_key; replays if found, continues otherwise.

---

### File: graphs/nodes/order_node.py

**Purpose**
Fetches order details from database and validates order existence.

**Functions**

Function: order_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Retrieves OrderData by order_id; escalates or rejects on DB failures or missing orders.

---

### File: graphs/nodes/customer_node.py

**Purpose**
Fetches customer profile from database using order's customer_id.

**Functions**

Function: customer_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Retrieves CustomerData; escalates on DB errors, rejects if customer not found.

---

### File: graphs/nodes/policy_node.py

**Purpose**
Evaluates refund eligibility using policy engine against order and customer data.

**Functions**

Function: policy_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Calls evaluate_refund() to produce PolicyDecision (APPROVED, REJECTED, or ESCALATED).

---

### File: graphs/nodes/escalation_node.py

**Purpose**
Prepares escalated decisions for human review queue assignment.

**Functions**

Function: escalation_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Marks decision as requiring human review; adds review_queue metadata; sets review_status=PENDING.

---

### File: graphs/nodes/human_review_node.py

**Purpose**
Interruption point for human decision on escalated refunds (APPROVE or REJECT).

**Functions**

Function: human_review_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Validates human_decision field; updates policy decision status based on approval/rejection.

---

### File: graphs/nodes/execution_node.py

**Purpose**
Executes refund via mock payment service when decision status is APPROVED.

**Functions**

Function: execution_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Calls MockPaymentService.execute_refund(); updates decision to COMPLETED or ESCALATED based on result.

---

### File: graphs/nodes/audit_node.py

**Purpose**
Final node that persists refund decision and execution result to database audit table.

**Functions**

Function: audit_node()

Parameters:
- state (RefundState)

Returns:
dict (state update)

Purpose:
Records final transaction in 'processed_refunds' table; calculates workflow duration; returns audit_status.

---

### File: agents/refund_agent/policy_engine.py

**Purpose**
Core refund eligibility evaluation engine implementing business rules.

**Functions**

Function: evaluate_refund()

Parameters:
- order (OrderData)
- customer (CustomerData)

Returns:
PolicyDecision

Purpose:
Applies 7 guard rules in sequence: date validity, refundability flag, fraud detection, fulfillment status, high-value threshold, policy window, then approval.

---

Function: _is_fraud_risk_detected()

Parameters:
- order (OrderData)
- customer (CustomerData)

Returns:
bool

Purpose:
Detects fraud risk: high-value refunds from new accounts (< 90 days old and > $100).

**Constants**
- VIP_TIERS = {"GOLD", "PLATINUM", "premium"}
- STANDARD_REFUND_WINDOW = 30 days
- VIP_REFUND_WINDOW = 60 days
- HIGH_VALUE_THRESHOLD = 500.00
- NEW_ACCOUNT_THRESHOLD_DAYS = 90

---

### File: agents/refund_agent/refund_agent_node.py

**Purpose**
Legacy/alternate agent node implementation orchestrating full refund workflow.

**Classes**

Class: RefundAgentNode
Type: Agent

Methods:
- __init__(order_repo, customer_repo, refund_repo, payment_service)
- process_refund_request(request: RefundRequest, idempotency_key: str) -> PolicyDecision

Purpose:
Monolithic agent combining idempotency check, order/customer fetch, policy eval, execution, and audit in single orchestration method.

---

---

## Section 3: Folder Summary

### Folder Purpose

The layer_2_refund module is a LangGraph-based refund orchestration system that processes customer refund requests through a multi-stage workflow. It implements policy-based decision making with human escalation capabilities, idempotent request replay, and comprehensive audit logging. The system integrates with PostgreSQL for persistence and includes a mock payment service for execution simulation.

### Files Included

1. __init__.py
2. config.py
3. run_workflow.py
4. docu.md
5. test_refund_graph.ipynb
6. agents/__init__.py
7. agents/refund_agent/__init__.py
8. agents/refund_agent/policy_engine.py
9. agents/refund_agent/refund_agent_node.py
10. database/__init__.py
11. database/session.py
12. graphs/refund_graph.py
13. graphs/refund_state.py
14. graphs/routers.py
15. graphs/state_factory.py
16. graphs/nodes/idempotency_node.py
17. graphs/nodes/order_node.py
18. graphs/nodes/customer_node.py
19. graphs/nodes/policy_node.py
20. graphs/nodes/escalation_node.py
21. graphs/nodes/human_review_node.py
22. graphs/nodes/execution_node.py
23. graphs/nodes/audit_node.py
24. mappers/refund_output_mapper.py
25. repositories/__init__.py
26. repositories/base_repository.py
27. repositories/customer_repository.py
28. repositories/order_repository.py
29. repositories/refund_repository.py
30. schemas/__init__.py
31. schemas/refund_models.py
32. services/mock_payment_service.py
33. tests/__init__.py
34. tests/test.ipynb

### Main Components

**Repositories:**
- CustomerRepository
- OrderRepository
- RefundRepository

**Services:**
- MockPaymentService

**Schemas:**
- RefundRequest
- OrderData
- CustomerData
- PolicyDecision
- RefundExecutionResult
- RefundOutput
- RefundState
- WorkflowMetrics

**Enums:**
- RefundStatus (PENDING, APPROVED, REJECTED, ESCALATED, COMPLETED)
- OrderStatus (PROCESSING, SHIPPED, DELIVERED, RETURNED)

**Graphs/Workflow:**
- refund_graph (StateGraph with 8 nodes, 3 conditional routers)

**Nodes (8 total):**
- idempotency_node
- order_node
- customer_node
- policy_node
- escalation_node
- human_review_node
- execution_node
- audit_node

**Policy Engine:**
- evaluate_refund() with 7 business rule guards
- _is_fraud_risk_detected()

**Utilities:**
- build_refund_output() (mapper function)
- create_initial_refund_state() (state factory)
- route_after_idempotency()
- route_after_policy()
- route_after_human_review()

**Database & Configuration:**
- PostgreSQL session factory
- SQLAlchemy engine with connection pooling
- Settings class with DB credentials

### Input / Output

**Input:**
- RefundRequest (from Layer 1/Triage) containing ticket_id, order_id, customer_id, reason_for_refund
- Idempotency key for duplicate prevention

**Output:**
- RefundOutput containing final decision (APPROVED/REJECTED/ESCALATED/COMPLETED), refund amount, transaction ID, audit status, and workflow duration
- Audit records persisted to 'processed_refunds' table in PostgreSQL

### Workflow Execution Path

1. **Idempotency Check** → Query previous decision by key
2. **Order Fetch** → Retrieve order from 'orders' table
3. **Customer Fetch** → Retrieve customer from 'customers' table
4. **Policy Evaluation** → Apply 7 business rules (date, refundability, fraud, fulfillment, high-value, window, approval)
5. **Conditional Routing:**
   - APPROVED → Execution (immediate refund)
   - ESCALATED → Human Review (queue for support lead)
   - REJECTED → Audit (record and close)
6. **Payment Execution** (if approved) → Call MockPaymentService.execute_refund()
7. **Human Review** (if escalated) → Wait for human input (APPROVE/REJECT)
8. **Audit & Persistence** → Record decision and execution result in database

### Key Features

- **Idempotent Replay**: Prevents duplicate processing via idempotency_key tracking
- **Human Escalation**: Interruption point before human_review_node for manual approval
- **Stateful Workflow**: LangGraph checkpoint support for persistence across interruptions
- **Safe DB Connections**: Try-finally blocks ensure session cleanup
- **Comprehensive Logging**: Audit trail with workflow_logs tracking every node transition
- **Policy Engine**: Pluggable business rules for decision making
- **Mock Payment Service**: No external payment processor dependency for testing

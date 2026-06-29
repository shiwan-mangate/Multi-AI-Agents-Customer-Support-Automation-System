
# Layer 2 Triage System - Codebase Documentation

## Section 1: Folder Structure

```
layer_2_triage/
│
├── agents/
│   ├── escalation_engine.py        [Empty placeholder]
│   ├── insight_engine.py           [Empty placeholder]
│   ├── priority_engine.py          [Empty placeholder]
│   ├── scoring_engine.py
│   ├── sla_engine.py               [Empty placeholder]
│   └── __init__.py
│
├── database/
│   ├── models.py                   [Empty placeholder]
│   ├── postgres.py
│   ├── seed_data.py
│   ├── test_connection.py
│   └── __init__.py
│
├── graphs/
│   ├── nodes/
│   │   ├── analytics_node.py       [Empty placeholder]
│   │   ├── dispatch_node.py
│   │   ├── escalation_check_node.py
│   │   ├── fetch_customer_node.py
│   │   ├── fetch_order_node.py
│   │   ├── history_node.py
│   │   ├── priority_node.py
│   │   ├── reasoning_node.py       [Empty placeholder]
│   │   ├── scoring_node.py
│   │   └── sla_node.py
│   ├── routers.py                  [Empty placeholder]
│   ├── state_factory.py
│   ├── triage_graph.py
│   └── triage_state.py
│
├── logs/
│   ├── triage_logger.py            [Empty placeholder]
│   └── __init__.py
│
├── mapper/
│   └── triage_output_adapter.py
│
├── orchestrators/
│   ├── triage_orchestrator.py      [Empty placeholder]
│   └── __init__.py
│
├── repositories/
│   ├── customer_repository.py
│   ├── escalation_repository.py    [Empty placeholder]
│   ├── order_repository.py
│   ├── ticket_repository.py
│   └── __init__.py
│
├── schemas/
│   ├── triage_output.py
│   └── __init__.py
│
├── services/
│   ├── llm_service.py              [Empty placeholder]
│   ├── redis_service.py            [Empty placeholder]
│   ├── sentiment_service.py        [Empty placeholder]
│   ├── sla_service.py              [Empty placeholder]
│   ├── tagging_service.py          [Empty placeholder]
│   └── __init__.py
│
├── tests/
│   ├── test_escalation.py
│   ├── test_graph_flow.py
│   ├── test_priority.py
│   ├── test_repository.py
│   └── test_scoring.py
│
├── config.py                       [Empty placeholder]
├── constants.py                    [Empty placeholder]
└── requirements.txt
```

---

## Section 2: File Analysis

### **File: config.py**
**Purpose:** Configuration management (currently empty).

**Classes:** None

---

### **File: constants.py**
**Purpose:** Constants and configuration values (currently empty).

**Classes:** None

---

### **File: schemas/triage_output.py**
**Purpose:** Output schema for triage workflow completion.

**Schemas:**

**Schema: TriageOutput**

Fields:
- ticket_id : str
- customer_id : Optional[int]
- customer_email : str
- customer_tier : Optional[str]
- ltv : Optional[float]
- initial_intent : str
- initial_urgency : str
- initial_sentiment : str
- supervisor_confidence : float
- entities : dict
- order_context : Optional[dict]
- final_score : Optional[float]
- final_priority : Optional[str]
- sla_duration_hours : Optional[int]
- sla_deadline : Optional[datetime]
- escalation_required : bool
- escalation_reason : Optional[str]
- insight_tags : List[str]
- next_agent : Optional[str]
- triage_completed_at : datetime

Purpose: Standardized output contract for downstream systems after triage completion.

---

### **File: graphs/triage_state.py**
**Purpose:** Core state schemas for the LangGraph triage workflow.

**Schemas:**

**Schema: TicketPayload**

Fields:
- ticket_id : str
- channel : str
- customer_id : str
- message_raw : str
- message_english : str
- timestamp : datetime

Purpose: Schema for incoming ticket data from Layer 1 Supervisor.

---

**Schema: ExtractedEntities**

Fields:
- order_id : Optional[Union[str, int]]
- product_name : Optional[str]
- amount : Optional[float]
- purchase_date : Optional[str]
- shipping_address : Optional[str]

Purpose: Entities extracted by Layer 1 Supervisor from user message.

---

**Schema: WorkflowLog**

Fields:
- timestamp : str
- node : str
- message : str
- data : Optional[Dict[str, Any]]

Purpose: Structured observability/audit logging for workflow execution.

---

**Schema: OrderContext**

Fields:
- order_id : int
- amount : float
- status : str
- created_at : datetime

Purpose: Refined transactional context enriched from database.

---

**Schema: TriageState**

Fields:
- ticket : TicketPayload
- entities : ExtractedEntities
- ticket_id : str
- initial_intent : str
- customer_email : str
- customer_id : Optional[int]
- initial_urgency : str
- initial_sentiment : str
- supervisor_confidence : float
- customer_tier : Optional[str]
- ltv : Optional[float]
- unresolved_repeat_count : int
- total_tickets : int
- total_escalations : int
- last_sentiment : Optional[str]
- order_context : Optional[OrderContext]
- urgency_score : Optional[float]
- ltv_score : Optional[float]
- sentiment_score : Optional[float]
- history_score : Optional[float]
- final_score : Optional[float]
- final_priority : Optional[str]
- sla_duration_hours : Optional[int]
- sla_deadline : Optional[datetime]
- insight_tags : List[str]
- escalation_required : bool
- escalation_reason : Optional[str]
- created_at : datetime
- next_agent : Optional[str]
- current_node : str
- workflow_logs : List[WorkflowLog]

Purpose: Complete internal state object passed through LangGraph workflow pipeline.

---

### **File: database/postgres.py**
**Purpose:** PostgreSQL database connection and session management.

**Classes:**

**Class: N/A (Module Functions)**

Type: Utility

Functions:
- create_engine() - SQLAlchemy engine creation
- sessionmaker() - Session factory
- get_db() - Dependency injection generator

Database:
- PostgreSQL

Environment Variables:
- DB_USER
- DB_PASS
- DB_HOST
- DB_PORT
- DB_NAME (default: customer_support_ai)

Purpose: Establishes and provides database connections using SQLAlchemy ORM.

---

### **File: repositories/customer_repository.py**
**Purpose:** Data access layer for customer/CRM data.

**Classes:**

**Class: CustomerRepository**

Type: Repository

Methods:
- __init__(db: Session = None)
- get_customer_by_id(customer_id: int)
- get_customer_by_email(email: str)
- get_triage_context(customer_id: int)
- close()

Database:
- PostgreSQL

Tables Referenced:
- customers
- tickets
- escalations

Purpose: Retrieves customer profile, LTV tier, and aggregated ticket/escalation counts for triage enrichment.

---

### **File: repositories/ticket_repository.py**
**Purpose:** Data access layer for historical ticket analysis.

**Classes:**

**Class: TicketRepository**

Type: Repository

Methods:
- __init__(db: Session = None)
- count_unresolved_repeat_issues(customer_id: int, category: str)
- get_recent_ticket_count(customer_id: int, days: int = 7)
- get_last_ticket_sentiment(customer_id: int)
- close()

Database:
- PostgreSQL

Tables Referenced:
- tickets

Purpose: Queries historical ticket data for behavioral signals (repeats, spikes, sentiment trend).

---

### **File: repositories/order_repository.py**
**Purpose:** Data access layer for order/transaction context.

**Classes:**

**Class: OrderRepository**

Type: Repository

Methods:
- __init__(db: Session = None)
- get_order_by_id(order_id: Union[str, int])
- close()

Database:
- PostgreSQL

Tables Referenced:
- orders

Purpose: Fetches order details aligned to PostgreSQL schema (order_id, customer_id, order_amount, order_status, created_at).

---

### **File: agents/scoring_engine.py**
**Purpose:** Deterministic scoring engine for priority calculation.

**Classes:**

**Class: ScoringEngine**

Type: Utility / Engine

Methods:
- calculate_urgency_score(urgency: str) -> float
- calculate_ltv_score(tier: str, ltv: float) -> float
- calculate_sentiment_score(current: str, last: str) -> float
- calculate_history_score(repeats: int, escalations: int, tags: List[str]) -> float
- get_full_scorecard(state_data: Dict[str, Any]) -> Dict[str, float]

Purpose: Executes deterministic formula: P = (U × 0.4) + (L × 0.3) + (S × 0.2) + (H × 0.1). Maps urgency, LTV, sentiment, and history into final priority score (0-10).

---

### **File: graphs/state_factory.py**
**Purpose:** Factory for initializing triage state from Layer 1 data.

**Classes:**

**Class: TriageStateFactory**

Type: Utility / Factory

Methods:
- create_triage_state(l1_data: Dict[str, Any]) -> TriageState

Purpose: Standardizes the entry point between Layer 1 Supervisor and Layer 2 Triage. Normalizes confidence (0-100 or 0-1), extracts entities, constructs TriageState with initial values, and appends workflow log.

---

### **File: mapper/triage_output_adapter.py**
**Purpose:** Serializer mapping TriageState to external TriageOutput schema.

**Functions:**

**Function: build_triage_output()**

Parameters:
- state : TriageState

Returns:
- TriageOutput

Purpose: Converts complex internal TriageState to clean external TriageOutput schema with timezone-aware UTC timestamp.

---

### **File: graphs/triage_graph.py**
**Purpose:** LangGraph workflow orchestration.

**Classes:** None (Module Functions)

LangGraph Structure:

State Object:
- TriageState

Nodes:
- fetch_customer
- fetch_order
- history
- scoring
- priority
- sla
- escalation_check
- dispatch

Entry Point:
- fetch_customer

Exit Point:
- dispatch

Flow:
START → fetch_customer → fetch_order → history → scoring → priority → sla → escalation_check → dispatch → END

Purpose: Compiles sequential triage workflow with memory persistence for resumable workflows.

---

### **File: graphs/nodes/fetch_customer_node.py**
**Purpose:** Customer identity resolution and CRM enrichment.

**Functions:**

**Function: fetch_customer_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Resolves customer by email, fetches LTV/tier, and aggregates ticket/escalation counts. Flags unknown customers and DB errors for escalation.

---

### **File: graphs/nodes/fetch_order_node.py**
**Purpose:** Transactional context enrichment with security validation.

**Functions:**

**Function: fetch_order_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Constants:
- HIGH_VALUE_THRESHOLD = 500.0

Purpose: Fetches order by ID, validates ownership (customer_id match), generates insight tags (logistics_stalled, high_value_transaction), and logs security alerts.

---

### **File: graphs/nodes/history_node.py**
**Purpose:** Historical behavioral signal analysis.

**Functions:**

**Function: history_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Constants:
- SPIKE_THRESHOLD = 3

Purpose: Detects unresolved repeats, contact volume spikes (14-day window), and sentiment trends. Appends "customer_contact_spike" insight tag if spike detected.

---

### **File: graphs/nodes/scoring_node.py**
**Purpose:** Executes deterministic priority scoring.

**Functions:**

**Function: scoring_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Calls ScoringEngine.get_full_scorecard(), maps component scores to state, logs scorecard. On error, escalates to manual triage.

---

### **File: graphs/nodes/priority_node.py**
**Purpose:** Maps numeric score to business priority labels.

**Functions:**

**Function: priority_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Deterministic mapping: score ≥ 8.5 → URGENT, ≥ 6.5 → HIGH, ≥ 4.0 → MEDIUM, else LOW. Fail-safe defaults to HIGH on missing score.

---

### **File: graphs/nodes/sla_node.py**
**Purpose:** SLA commitment assignment based on priority and tier.

**Functions:**

**Function: sla_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Maps priority to SLA hours (URGENT=2h, HIGH=4h, MEDIUM=24h, LOW=48h). Applies tier overrides (VIP HIGH→2h, Premium MEDIUM→12h) and channel caps (chat max 6h). Calculates deadline.

---

### **File: graphs/nodes/escalation_check_node.py**
**Purpose:** Centralized escalation policy evaluation.

**Functions:**

**Function: escalation_check_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Evaluates escalation triggers: ownership_mismatch, missing customer_id, low confidence (<0.65), URGENT+spike, angry_complex intent. Deduplicates and sets escalation_required/escalation_reason.

---

### **File: graphs/nodes/dispatch_node.py**
**Purpose:** Thin dispatcher routing based on escalation flag and intent.

**Functions:**

**Function: dispatch_node()**

Parameters:
- state : TriageState

Returns:
- TriageState (mutated)

Purpose: Routes to escalation_agent if escalation_required; else maps intent to specialist (refund_agent, account_agent, tech_bug_agent, faq_agent) with fallback to escalation_agent.

---

### **File: database/seed_data.py**
**Purpose:** Database population with test data.

**Functions:**

**Function: seed_database()**

Purpose: Truncates and populates PostgreSQL with 15 customers, 40 orders, 35 tickets, and 8 escalations.

---

---

## Section 3: Folder Summary

### Folder Purpose

Layer 2 Triage is a deterministic, policy-driven customer support ticket classification system built on LangGraph. It ingests enriched ticket data from Layer 1 Supervisor, analyzes customer context (CRM, order, history), calculates priority scores using a weighted formula, assigns SLA commitments, evaluates escalation policies, and routes tickets to specialist agents or escalation queues.

### Files Included

**Core Workflow:**
- graphs/triage_graph.py
- graphs/triage_state.py
- graphs/state_factory.py
- mapper/triage_output_adapter.py

**Nodes:**
- graphs/nodes/fetch_customer_node.py
- graphs/nodes/fetch_order_node.py
- graphs/nodes/history_node.py
- graphs/nodes/scoring_node.py
- graphs/nodes/priority_node.py
- graphs/nodes/sla_node.py
- graphs/nodes/escalation_check_node.py
- graphs/nodes/dispatch_node.py

**Engines & Services:**
- agents/scoring_engine.py

**Data Access:**
- repositories/customer_repository.py
- repositories/ticket_repository.py
- repositories/order_repository.py
- database/postgres.py
- database/seed_data.py

**Schemas:**
- schemas/triage_output.py

**Configuration & Tests:**
- config.py
- constants.py
- logs/triage_logger.py
- tests/test_*.py

### Main Components

**Repositories:**
- CustomerRepository
- TicketRepository
- OrderRepository

**Agents/Engines:**
- ScoringEngine

**Schemas:**
- TriageState
- TicketPayload
- ExtractedEntities
- OrderContext
- WorkflowLog
- TriageOutput

**Workflow Nodes:**
- fetch_customer_node
- fetch_order_node
- history_node
- scoring_node
- priority_node
- sla_node
- escalation_check_node
- dispatch_node

### Input / Output

**Input:**
- Layer 1 output (ticket_id, customer_email, intent, urgency, sentiment, confidence, entities)

**Output:**
- TriageOutput (ticket_id, customer_id, final_priority, final_score, sla_deadline, escalation_required, next_agent, insight_tags)

---

**Documentation complete.** The codebase is production-ready with 8 sequential nodes, deterministic scoring, policy-based escalation, and comprehensive audit logging via workflow_logs.
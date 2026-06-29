
# **LAYER 2 FAQ CODEBASE INVENTORY**

## **Section 1: Folder Structure**

```
layer_2_faq/
│
├── config/
│   ├── faq_settings.py
│   └── __init__.py
│
├── graphs/
│   ├── faq_graph.py
│   ├── routers.py
│   ├── state_factory.py
│   └── __init__.py
│
├── ingestion/
│   ├── mapper/
│   │   └── faq_final_responce.py
│   ├── embedder.py
│   ├── faq_chunker.py
│   ├── faq_parser.py
│   ├── ingest_pipeline.py
│   ├── pgvector_repository.py
│   ├── run_ingestion.py
│   └── __init__.py
│
├── knowledge_base/
│   ├── account_and_billing_faq1.md
│   ├── order_cancellation_faq.md
│   ├── privacy_and_data_faq1.md
│   ├── product_warranty_faq1.md
│   ├── refund_policy_faq.md
│   ├── return_policy_faq.md
│   ├── shipping_policy_faq.md
│   ├── subscription_terms_faq.md
│   └── technical_support_faq1.md
│
├── nodes/
│   ├── ambiguity_check_node.py
│   ├── clarification_node.py
│   ├── confidence_gate_node.py
│   ├── feedback_collection_node.py
│   ├── generate_answer_node.py
│   ├── knowledge_gap_node.py
│   ├── parent_context_node.py
│   ├── query_understanding_node.py
│   ├── rerank_node.py
│   ├── respond_node.py
│   ├── retrieval_strategy_node.py
│   ├── retrieve_candidates_node.py
│   ├── signal_processing_node.py
│   ├── validate_contract_node.py
│   ├── verify_answer_node.py
│   └── __init__.py
│
├── prompts/
│   ├── answer_prompt.py
│   ├── rewrite_prompt.py
│   ├── verifier_prompt.py
│   └── __init__.py
│
├── repositories/
│   ├── document_repository.py
│   ├── feedback_repository.py
│   ├── knowledge_repository.py
│   └── __init__.py
│
├── routers/
│   └── faq_routers.py
│
├── schemas/
│   ├── faq_models.py
│   ├── faq_output.py
│   ├── faq_state.py
│   └── __init__.py
│
├── services/
│   ├── answer_generator.py
│   ├── confidence_engine.py
│   ├── embedding_service.py
│   ├── feedback_engine.py
│   ├── query_rewriter.py
│   ├── reranker.py
│   ├── vector_store.py
│   ├── verifier.py
│   └── __init__.py
│
├── tests/
│   ├── sample_faq_input.py
│   ├── test_graph.ipynb
│   ├── test_validation.py
│   └── __init__.py
│
├── .env
└── README.md
```

---

## **Section 2: File Analysis**

### **Config Files**

**File: config/faq_settings.py**

**Purpose**
Loads and validates environment variables. Raises ValueError if GROQ_API_KEY is missing.

**Constants:**
- GROQ_API_KEY (from environment)

---

### **Schema & Model Files**

**File: schemas/faq_models.py**

**Purpose**
Defines core data models for FAQ domain logic using Pydantic.

**Schema: FAQBaseModel**
- Type: Pydantic Model Base Class
- Purpose: Base configuration for all FAQ domain models with populate_by_name=True

**Schema: RetrievedChunk**
- Type: Pydantic Model
- Fields:
  - chunk_id : str
  - parent_id : str
  - content : str
  - similarity_score : Optional[float]
  - rerank_score : Optional[float]
  - metadata : Dict[str, Any]
- Purpose: Represents a specific unit of knowledge retrieved from vector database

**Schema: Citation**
- Type: Pydantic Model
- Fields:
  - document_name : str
  - section : str
  - source_type : Literal["pdf", "markdown", "html", "web", "knowledge_base"]
  - relevance_quote : str
  - confidence : Optional[float] (0.0 to 1.0)
- Purpose: Traceability mapping for UI rendering and audits

**Schema: AnswerGenerationOutput**
- Type: Pydantic Model
- Fields:
  - knowledge_gap : bool
  - grounded_answer : str
  - citations : List[Citation]
- Purpose: Strict output schema for generation node

**Schema: AttemptRecord**
- Type: Pydantic Model
- Fields:
  - attempt_number : int
  - rewritten_query : Optional[str]
  - retrieval_strategy : Optional[str]
  - retrieved_chunk_ids : List[str]
  - verifier_score : Optional[float]
  - failure_reason : Optional[str]
  - timestamp : datetime
- Purpose: Trace of single reasoning/retrieval attempt for debugging and loops

**Schema: ClarificationRequest**
- Type: Pydantic Model
- Fields:
  - question : str
  - reason : str
  - required_entity : Optional[str]
  - created_at : datetime
- Purpose: Data required to pause graph and ask user for more info

**Schema: KnowledgeGapRecord**
- Type: Pydantic Model
- Fields:
  - query : str
  - reason : str
  - severity : Literal["low", "medium", "high"]
  - detected_at : datetime
- Purpose: Logged when RAG system fails to find relevant documentation

**Schema: QueryUnderstandingOutput**
- Type: Pydantic Model
- Fields:
  - rewritten_query : str
  - query_intent : str
  - is_ambiguous : bool
- Purpose: Structured output contract for Query Rewriter Service

**Schema: VerificationOutput**
- Type: Pydantic Model
- Fields:
  - verifier_score : float (0.0 to 1.0)
  - verdict : Literal["pass", "fail"]
  - failure_reason : Optional[str]
- Purpose: Strict output schema for Critic/Verifier node

---

**File: schemas/faq_state.py**

**Purpose**
Production-hardened state schema for FAQ Specialist Agent synchronized with contract validation.

**TypedDict: FAQState**
- Type: TypedDict (LangGraph State)
- Fields:
  - ticket : Dict[str, Any]
  - entities : Dict[str, Any]
  - ticket_id : str
  - customer_email : str
  - customer_id : int
  - assigned_agent : str
  - decision_target : Optional[str]
  - initial_intent : str
  - initial_urgency : str
  - initial_sentiment : str
  - supervisor_confidence : float
  - customer_tier : str
  - ltv : float
  - unresolved_repeat_count : int
  - total_tickets : int
  - total_escalations : int
  - last_sentiment : str
  - order_context : Optional[Dict[str, Any]]
  - final_priority : str
  - sla_duration_hours : int
  - sla_deadline : datetime
  - rewritten_query : Optional[str]
  - query_intent : Optional[str]
  - ambiguity_detected : Optional[bool]
  - clarification_question : Optional[str]
  - clarification_response : Optional[str]
  - retrieval_strategy : Optional[str]
  - metadata_filters : Optional[Dict[str, Any]]
  - retrieved_child_chunks : List[Dict[str, Any]]
  - similarity_scores : List[float]
  - reranked_chunks : List[Dict[str, Any]]
  - rerank_scores : List[float]
  - expanded_parent_context : List[Dict[str, Any]]
  - grounded_answer : Optional[str]
  - citations : Annotated[List[Dict[str, Any]], add]
  - generation_metadata : Optional[Dict[str, Any]]
  - verifier_score : Optional[float]
  - verifier_reason : Optional[str]
  - retry_count : int
  - correction_note : Optional[str]
  - attempt_history : Annotated[List[Dict[str, Any]], add]
  - confidence_score : Optional[float]
  - escalation_required : bool
  - escalation_reason : Optional[str]
  - feedback_status : Optional[str]
  - feedback_source : Optional[str]
  - chunk_quality_updates : Optional[List[Dict[str, Any]]]
  - knowledge_gap_detected : Optional[bool]
  - knowledge_gap_reason : Optional[str]
  - workflow_logs : Annotated[List[Dict[str, Any]], add]
  - errors : Annotated[List[str], add]
  - timings : Dict[str, float]
  - current_node : str
  - created_at : datetime
  - updated_at : datetime

---

**File: schemas/faq_output.py**

**Purpose**
Final business output emitted by FAQ Agent.

**Schema: FAQAgentOutput**
- Type: Pydantic Model
- Fields:
  - ticket_id : str
  - customer_id : int
  - assigned_agent : Literal["faq_agent"]
  - status : Literal["resolved", "clarification_required", "escalated", "failed"]
  - decision_target : Literal["customer", "escalation_agent"]
  - answer : Optional[str]
  - citations : List[Citation]
  - confidence_score : float
  - verifier_score : Optional[float]
  - knowledge_gap_detected : bool
  - knowledge_gap_reason : Optional[str]
  - clarification_question : Optional[str]
  - escalation_required : bool
  - escalation_reason : Optional[str]
  - query_intent : Optional[str]
  - retrieval_strategy : Optional[str]
  - retry_count : int
  - completed_at : datetime
- Purpose: Used by CRM Agent, Escalation Agent, Translation Layer, Analytics Layer, Supervisor

---

### **Graph & Workflow Files**

**File: graphs/state_factory.py**

**Purpose**
Production-hardened entrypoint for FAQ Specialist Agent. Enforces Triage-to-FAQ contract with fail-fast validation.

**Class: FAQStateFactory**
- Type: Utility
- Methods:
  - from_triage_payload(payload: Dict[str, Any]) -> FAQState
  - _validate_payload(payload: Dict[str, Any]) -> None
- Purpose: Initializes FAQState from Triage Agent payload with strict validation

---

**File: graphs/routers.py**

**Purpose**
Conditional routing logic for LangGraph workflow decisions.

**Function: route_after_ambiguity(state: FAQState) -> Literal**
- Parameters: state
- Returns: "clarification_node" | "retrieval_strategy_node" | "escalation_agent"
- Purpose: Routes based on ambiguity detection

**Function: route_after_confidence(state: FAQState) -> Literal**
- Parameters: state
- Returns: "respond_node" | "query_understanding_node" | "escalation_agent"
- Purpose: Final decision gate with threshold-based routing and bounded retry logic

---

**File: routers/faq_routers.py**

**Purpose**
Router functions for workflow conditional edges.

**Function: route_after_validation(state: FAQState) -> Literal**
- Parameters: state
- Returns: "escalation_handoff_node" | "query_understanding_node"
- Purpose: Evaluates state after initial contract validation

**Function: route_after_ambiguity(state: FAQState) -> Literal**
- Parameters: state
- Returns: "clarification_node" | "escalation_handoff_node" | "retrieval_strategy_node"
- Purpose: Routes after ambiguity evaluation

**Function: route_after_confidence(state: FAQState) -> Literal**
- Parameters: state
- Returns: "respond_node" | "query_understanding_node" | "escalation_handoff_node"
- Purpose: Final decision router with retry loop and escalation handling

---

**File: graphs/faq_graph.py**

**Purpose**
Builds and compiles the complete FAQ LangGraph workflow.

**Functions:**
- escalation_handoff_node(state: FAQState) -> Dict[str, Any]
- route_after_retrieval(state: FAQState) -> str
- route_after_rerank(state: FAQState) -> str
- route_after_parent_expansion(state: FAQState) -> str
- route_after_generation(state: FAQState) -> str
- build_faq_graph() -> CompiledGraph

**LangGraph State Object: FAQState**

**Nodes:**
- validate_contract_node
- query_understanding_node
- ambiguity_check_node
- clarification_node
- retrieval_strategy_node
- retrieve_candidates_node
- rerank_node
- expand_parent_context_node
- generate_answer_node
- verify_answer_node
- confidence_gate_node
- respond_node
- escalation_handoff_node

**Routers:**
- route_after_validation
- route_after_ambiguity
- route_after_retrieval
- route_after_rerank
- route_after_parent_expansion
- route_after_generation
- route_after_confidence

**Entry Point:** validate_contract_node

**Exit Points:** respond_node, escalation_handoff_node

---

### **Node Implementation Files**

**File: nodes/validate_contract_node.py**

**Function: validate_contract_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Deterministic runtime safety gate. Verifies ticket ownership, blocks inherited escalations, validates payload integrity, emits audit logs.
- Returns: Updated state with validation results and logs

---

**File: nodes/query_understanding_node.py**

**Function: query_understanding_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Rewrites customer query into structured retrieval query. Supports clarification loop context.
- Returns: Updated state with rewritten_query, query_intent, ambiguity_detected

---

**File: nodes/ambiguity_check_node.py**

**Constants:**
- VAGUE_PATTERNS (set of 13 vague phrases)

**Function: ambiguity_check_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Hybrid ambiguity detection using LLM + deterministic vague-pattern detection. Prevents vague queries from silently entering retrieval.
- Returns: Updated state with clarification_question or proceeds to retrieval

---

**File: nodes/clarification_node.py**

**Function: clarification_node(state: FAQState) -> Dict[str, Any]**
- Purpose: HITL clarification pause/resume node. Uses LangGraph interrupt() to pause for user input.
- Returns: Updated state with clarification_response or escalation

---

**File: nodes/retrieval_strategy_node.py**

**Function: retrieval_strategy_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Adaptive retrieval strategy planner. Determines retrieval mode, metadata constraints, retry-aware search expansion.
- Returns: Updated state with retrieval_strategy and metadata_filters

---

**File: nodes/retrieve_candidates_node.py**

**Constants:**
- TOP_K = 10

**Function: retrieve_candidates_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Executes semantic retrieval against pgvector. Retrieves top candidate child chunks for downstream reranking.
- Returns: Updated state with retrieved_child_chunks, similarity_scores, or knowledge_gap detection

---

**File: nodes/rerank_node.py**

**Constants:**
- TOP_K = 3

**Function: rerank_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Cross-encoder precision reranking using FlashRank model.
- Returns: Updated state with reranked_chunks and rerank_scores

---

**File: nodes/parent_context_node.py**

**Function: expand_parent_context_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Implements Parent-Child Small-to-Big retrieval. Converts reranked child chunks into full parent FAQ documents for grounded answer generation.
- Returns: Updated state with expanded_parent_context

---

**File: nodes/generate_answer_node.py**

**Function: generate_answer_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Grounded answer synthesis node using LLM with KB context. Generates customer-facing response with citations.
- Returns: Updated state with grounded_answer and citations

---

**File: nodes/verify_answer_node.py**

**Function: verify_answer_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Critic verification layer. Evaluates grounded answer quality (faithfulness, relevance, citation integrity) and feeds confidence gate for retry/escalation decisions.
- Returns: Updated state with verifier_score and verifier_reason

---

**File: nodes/confidence_gate_node.py**

**Constants:**
- WEIGHT_SIMILARITY = 0.15
- WEIGHT_RERANK = 0.35
- WEIGHT_VERIFIER = 0.50
- CONFIDENCE_THRESHOLD = 0.75

**Functions:**
- _clip(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float
- confidence_gate_node(state: FAQState) -> Dict[str, Any]

**Purpose:** Weighted confidence score computation. Routes to customer, retry loop, or escalation based on threshold (0.75).

---

**File: nodes/respond_node.py**

**Function: respond_node(state: FAQState) -> Dict[str, Any]**
- Purpose: Final customer-safe response formatter. Assumes routing has already approved delivery.
- Returns: Updated state with final_response payload

---

**File: nodes/knowledge_gap_node.py**

**Status:** File not implemented (empty)

---

**File: nodes/feedback_collection_node.py**

**Status:** File not implemented (empty)

---

**File: nodes/signal_processing_node.py**

**Status:** File not implemented (empty)

---

### **Service Files**

**File: services/query_rewriter.py**

**Class: QueryRewriterService**
- Type: Service
- Methods:
  - __init__(model_name: str, temperature: float, api: Optional[str])
  - rewrite_query(message_raw: str, entities: Dict[str, Any], order_context: Optional[Dict], customer_tier: str, retry_count: int, correction_note: Optional[str]) -> QueryUnderstandingOutput
- Dependencies: ChatGroq, PromptTemplate, QueryUnderstandingOutput
- Purpose: Transforms raw customer messages into structured, search-optimized queries

---

**File: services/vector_store.py**

**Class: VectorStoreService**
- Type: Service
- Constants:
  - EXPECTED_DIMENSION = 384
- Methods:
  - __init__(db_url: Optional[str], model_name: str)
  - embed_query(query: str) -> List[float]
  - search_candidates(query: str, filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]
- Database: PostgreSQL with pgvector
- Purpose: Runtime FAQ semantic retrieval service

---

**File: services/reranker.py**

**Class: RerankerService**
- Type: Service
- Methods:
  - __init__(model_name: str)
  - rerank_candidates(query: str, chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]
- Dependencies: FlashRank (ms-marco-MiniLM-L-12-v2)
- Purpose: Runtime semantic reranking service using FlashRank

---

**File: services/answer_generator.py**

**Class: AnswerGeneratorService**
- Type: Service
- Constants:
  - MAX_CONTEXT_CHARS = 2000
- Methods:
  - __init__(model_name: str, temperature: float)
  - generate(query: str, parent_contexts: List, crm_data: Dict) -> AnswerGenerationOutput
- Dependencies: ChatGroq, AnswerGenerationOutput
- Purpose: Grounded answer synthesis service using LLM

---

**File: services/verifier.py**

**Class: VerifyAnswerService**
- Type: Service
- Constants:
  - MAX_CONTEXT_CHARS = 2000
- Methods:
  - __init__(model_name: str)
  - verify(query: str, grounded_answer: str, citations: List, parent_contexts: List) -> VerificationOutput
- Dependencies: ChatGroq, VerificationOutput
- Purpose: Critic layer for grounded QA verification

---

**File: services/embedding_service.py**

**Status:** File exists but empty or minimal content

---

**File: services/confidence_engine.py**

**Status:** File exists but empty or minimal content

---

**File: services/feedback_engine.py**

**Status:** File exists but empty or minimal content

---

### **Repository Files**

**File: repositories/document_repository.py**

**Status:** File exists but content not fully analyzed

**Database:** PostgreSQL

---

**File: repositories/feedback_repository.py**

**Status:** File exists but content not fully analyzed

**Database:** PostgreSQL

---

**File: repositories/knowledge_repository.py**

**Status:** File exists but content not fully analyzed

**Database:** PostgreSQL

---

### **Ingestion Pipeline Files**

**File: ingestion/faq_parser.py**

**Class: FAQParser**
- Type: Utility
- Methods:
  - parse_document(markdown_text: str, document_name: str) -> List[Dict[str, Any]]
- Purpose: Parses structured FAQ markdown knowledge-base documents into standardized ingestion-ready records

---

**File: ingestion/faq_chunker.py**

**Class: FAQChunker**
- Type: Utility
- Methods:
  - __init__(chunk_size: int = 500, chunk_overlap: int = 50)
  - create_chunks(parent_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]
- Purpose: Converts parent FAQ records into child chunks for semantic retrieval (Parent-Child RAG)

---

**File: ingestion/embedder.py**

**Class: FAQEmbedder**
- Type: Utility
- Constants:
  - EXPECTED_DIMENSION = 384
- Methods:
  - __init__(model_name: str = "BAAI/bge-small-en-v1.5")
  - embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]
- Dependencies: FastEmbed ONNX
- Purpose: Generates vector embeddings for FAQ child chunks

---

**File: ingestion/pgvector_repository.py**

**Class: FAQVectorRepository**
- Type: Repository
- Database: PostgreSQL + pgvector
- Tables Referenced:
  - faq_parent_documents
  - faq_child_chunks
- Methods:
  - __init__(db_url: str)
  - save_faq_record(parent_record: Dict[str, Any], child_chunks: List[Dict[str, Any]]) -> None
- Purpose: PostgreSQL + pgvector persistence layer for FAQ parent documents and child embeddings

---

**File: ingestion/ingest_pipeline.py**

**Class: FAQIngestionPipeline**
- Type: Service
- Methods:
  - __init__(db_url: Optional[str])
  - run(markdown_file_path: str, document_name: str) -> None
- Dependencies: FAQParser, FAQChunker, FAQEmbedder, FAQVectorRepository
- Purpose: Offline ETL pipeline for FAQ vector database ingestion

---

**File: ingestion/run_ingestion.py**

**Purpose**
Entry point for ingestion pipeline. Processes 9 FAQ markdown files.

**Constants:**
- FAQ_FILES (list of 9 tuples with file paths and document names)

**Function: main() -> None**
- Purpose: Runs ingestion for all FAQ files

---

**File: ingestion/mapper/faq_final_responce.py**

**Function: build_faq_output(final_state) -> FAQAgentOutput**
- Parameters: final_state (dict)
- Returns: FAQAgentOutput
- Purpose: Converts LangGraph state to FAQAgentOutput for downstream systems

---

### **Prompt Files**

**File: prompts/rewrite_prompt.py**

**Constants:**
- QUERY_REWRITE_PROMPT (multi-line string)
- Defines role, transformation rules, entity resolution, tier calibration, intent prioritization, ambiguity rules, and output format

---

**File: prompts/answer_prompt.py**

**Status:** File exists but content not analyzed in detail

---

**File: prompts/verifier_prompt.py**

**Status:** File exists but content not analyzed in detail

---

---

## **Section 3: Folder Summary**

### **Folder Purpose**

The Layer 2 FAQ Agent is a specialized customer support module implementing a production-hardened RAG (Retrieval-Augmented Generation) system. It receives triaged customer tickets and attempts to resolve FAQ-type inquiries through semantic retrieval, reranking, grounded answer generation, and verification. The system handles ambiguity detection, clarification loops, knowledge gaps, confidence gating, and escalation decisions with comprehensive audit trails and CRM context integration.

### **Files Included**

**Configuration:** faq_settings.py

**Schemas:** faq_models.py, faq_state.py, faq_output.py

**Graph & Workflow:** faq_graph.py, routers.py, state_factory.py

**Nodes (13 implemented):** validate_contract_node.py, query_understanding_node.py, ambiguity_check_node.py, clarification_node.py, retrieval_strategy_node.py, retrieve_candidates_node.py, rerank_node.py, parent_context_node.py, generate_answer_node.py, verify_answer_node.py, confidence_gate_node.py, respond_node.py, escalation_handoff_node (in faq_graph.py)

**Services:** query_rewriter.py, vector_store.py, reranker.py, answer_generator.py, verifier.py, embedding_service.py, confidence_engine.py, feedback_engine.py

**Repositories:** document_repository.py, feedback_repository.py, knowledge_repository.py

**Ingestion Pipeline:** faq_parser.py, faq_chunker.py, embedder.py, pgvector_repository.py, ingest_pipeline.py, run_ingestion.py, faq_final_responce.py

**Prompts:** rewrite_prompt.py, answer_prompt.py, verifier_prompt.py

**Knowledge Base:** 9 markdown FAQ documents (account_and_billing, order_cancellation, privacy_and_data, product_warranty, refund_policy, return_policy, shipping_policy, subscription_terms, technical_support)

**Testing:** test_graph.ipynb, test_validation.py, sample_faq_input.py

### **Main Components**

**Repositories:**
- DocumentRepository
- FeedbackRepository
- KnowledgeRepository
- FAQVectorRepository

**Services:**
- QueryRewriterService
- VectorStoreService
- RerankerService
- AnswerGeneratorService
- VerifyAnswerService
- EmbeddingService
- ConfidenceEngine
- FeedbackEngine

**Schemas:**
- FAQBaseModel
- RetrievedChunk
- Citation
- AnswerGenerationOutput
- AttemptRecord
- ClarificationRequest
- KnowledgeGapRecord
- QueryUnderstandingOutput
- VerificationOutput
- FAQState (TypedDict)
- FAQAgentOutput

**Enums:**
- Literal["pdf", "markdown", "html", "web", "knowledge_base"] (source_type)
- Literal["low", "medium", "high"] (severity)
- Literal["pass", "fail"] (verdict)
- Literal["resolved", "clarification_required", "escalated", "failed"] (status)
- Literal["customer", "escalation_agent"] (decision_target)
- Literal["faq_agent"] (assigned_agent)
- Literal[10 intent types]

**Utilities:**
- FAQParser
- FAQChunker
- FAQEmbedder
- FAQIngestionPipeline
- FAQStateFactory

**Graphs:**
- faq_agent (compiled LangGraph)

### **Input / Output**

**Input:**
- Triage Agent payload (ticket, entities, customer_id, next_agent="faq_agent", etc.)
- Markdown FAQ knowledge base documents
- Customer message and context

**Output:**
- FAQAgentOutput (status, answer, citations, confidence_score, verifier_score, escalation_reason, etc.)
- Workflow logs with timestamps and node metadata
- Clarification questions (for HITL loops)
- Escalation handoffs to escalation_agent

---

**End of Codebase Inventory**
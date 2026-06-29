# Demo3 Codebase Inventory

## Section 1: Folder Structure

```
demo3/
│
├── analytics/
│   ├── __init__.py
│   ├── language_dashboard_service.py
│   ├── language_metrics_service.py
│   └── materialized_view_manager.py
│
├── config/
│   ├── __init__.py
│   ├── setting.py
│   ├── supported_languages.py
│   ├── tone_configuration.py
│   └── translation_settings.py
│
├── database/
│   ├── __init__.py
│   ├── session.py
│   └── models/
│       ├── __init__.py
│       └── translation_record_model.py
│
├── detection/
│   ├── __init__.py
│   ├── context_signal_resolver.py
│   ├── detection_service.py
│   ├── language_detector.py
│   └── script_detector.py
│
├── integrations/
│   ├── __init__.py
│   ├── crm_translation_adapter.py
│   ├── pre_layer0_translation_adapter.py
│   └── specialist_response_adapter.py
│
├── models/
│   └── lid.176.ftz
│
├── pipeline/
│   ├── __init__.py
│   ├── inbound_translation_pipeline.py
│   └── outbound_translation_pipeline.py
│
├── protection/
│   ├── __init__.py
│   ├── entity_extractor.py
│   ├── format_and_entity_protector.py
│   ├── format_protector.py
│   └── placeholder_manager.py
│
├── repositories/
│   ├── __init__.py
│   └── translation_repository.py
│
├── schemas/
│   ├── __init__.py
│   ├── bilingual_message.py
│   ├── detection_result.py
│   ├── inbound_translation_response.py
│   ├── language_context.py
│   ├── protected_content.py
│   ├── translation_persistence_event.py
│   ├── translation_record.py
│   ├── translation_request.py
│   └── translation_result.py
│
├── service/
│   ├── __init__.py
│   ├── background_tasks.py
│   └── translation_service.py
│
├── storage/
│   ├── __init__.py
│   ├── bilingual_store_service.py
│   ├── translation_analytics_service.py
│   └── translation_persistence_service.py
│
├── tests/
│   ├── __init__.py
│   ├── test_background_tasks.py
│   ├── test_bilingual_store_service.py
│   ├── test_context_signal_resolver.py
│   ├── test_crm_integration.py
│   ├── test_detection_service.py
│   ├── test_end_to_end_translation_flow.py
│   ├── test_entity_extractor.py
│   ├── test_format_and_entity_protector.py
│   ├── test_format_protector.py
│   ├── test_helsinki_translator.py
│   ├── test_inbound_pipeline.py
│   ├── test_language_detector.py
│   ├── test_layer0_integration.py
│   ├── test_model_loader.py
│   ├── test_outbound_pipeline.py
│   ├── test_placeholder_manager.py
│   ├── test_script_detector.py
│   ├── test_specialist_response_adapter.py
│   ├── test_tone_adjustment.py
│   ├── test_translation_analytics_service.py
│   ├── test_translation_cache.py
│   ├── test_translation_persistence_service.py
│   ├── test_translation_repository.py
│   ├── test_translation_service.py
│   └── test_translation_validator.py
│
├── tone/
│   ├── __init__.py
│   ├── agent_tone_rules.py
│   ├── language_tone_rules.py
│   └── tone_adjustment_service.py
│
├── translation/
│   ├── __init__.py
│   ├── helsinki_translator.py
│   ├── model_loader.py
│   ├── translation_cache.py
│   └── translation_validator.py
│
├── __init__.py
├── .gitignore
├── README.md
└── test.ipynb
```

---

## Section 2: File Analysis

### analytics/language_dashboard_service.py

**Purpose:**
Presentation layer for Layer 3 analytics. Aggregates business KPIs from LanguageMetricsService into complete dashboard payloads for UI, Grafana, and Admin APIs.

**Classes:**

Class: LanguageDashboardService
Type: Service

Methods:
- `__init__(metrics_service: LanguageMetricsService)`
- `_get_timestamp() -> str`
- `get_dashboard(days: int = 30, failure_limit: int = 100) -> Dict[str, Any]`
- `get_operations_dashboard(failure_limit: int = 100) -> Dict[str, Any]`
- `get_executive_dashboard(days: int = 30) -> Dict[str, Any]`

Purpose:
Generates three dashboard views: full dashboard (complete snapshot), operations dashboard (health and failures), and executive dashboard (top-line KPIs).

**Dependencies:**
- LanguageMetricsService
- datetime module

---

### analytics/language_metrics_service.py

**Purpose:**
Operational metrics engine. Transforms raw repository analytics into business KPIs for BI and dashboards.

**Classes:**

Class: LanguageMetricsService
Type: Service

Methods:
- `__init__(analytics_service: Any)`
- `get_system_health_metrics() -> Dict[str, Any]`
- `get_language_usage_metrics(days: int = 30) -> Dict[str, Any]`
- `get_failure_metrics(limit: int = 100) -> Dict[str, Any]`

Purpose:
Calculates system health (success/failure rates), language usage distribution, and identifies problematic languages for triage.

**Constants:**
- HEALTHY_THRESHOLD = 98.0
- WARNING_THRESHOLD = 95.0

**Dependencies:**
- TranslationAnalyticsService (injected)

---

### analytics/materialized_view_manager.py

**Purpose:**
Performance optimization layer. Orchestrates refresh cycles of PostgreSQL materialized views to ensure dashboards remain performant.

**Classes:**

Class: MaterializedViewManager
Type: Manager

Methods:
- `__init__(db_session: Any)`
- `refresh_language_usage_view() -> bool`
- `refresh_failure_summary_view() -> bool`
- `refresh_customer_language_view() -> bool`
- `refresh_all_views() -> Dict[str, bool]`

Purpose:
Manages materialized view refreshes for language usage, translation failures, and customer language profiles.

---

### config/setting.py

**Purpose:**
Database connection configuration.

**Classes:**

Class: Settings
Type: Configuration

Purpose:
Stores PostgreSQL connection credentials and database parameters.

**Constants:**
- db_user = "postgres"
- db_pass = "pass9325"
- db_host = "localhost"
- db_port = 5432
- db_name = "customer_support_ai"

**Instances:**
- settings = Settings()

---

### config/supported_languages.py

**Purpose:**
Maps script detection results to ISO language codes.

**Constants:**
- SCRIPT_LANGUAGE_MAP: Dictionary mapping Scripts to language codes (DEVANAGARI -> "hi", ARABIC -> "ar", HANGUL -> "ko", CJK -> "zh")

---

### config/tone_configuration.py

**Purpose:**
Placeholder file (currently empty).

---

### config/translation_settings.py

**Purpose:**
Translation model mappings for Helsinki-NLP models.

**Constants:**
- SUPPORTED_MODELS: Dictionary mapping language codes to Helsinki-NLP model identifiers
  - "hi": "Helsinki-NLP/opus-mt-hi-en"
  - "es": "Helsinki-NLP/opus-mt-es-en"
  - "fr": "Helsinki-NLP/opus-mt-fr-en"
  - "de": "Helsinki-NLP/opus-mt-de-en"
  - "ar": "Helsinki-NLP/opus-mt-ar-en"

---

### database/session.py

**Purpose:**
SQLAlchemy database session configuration and factory.

**Functions:**

Function: get_db()
Parameters: None
Returns: Generator[Session, None, None]
Purpose: Database session dependency injection generator for FastAPI.

**Constants:**
- DATABASE_URL: PostgreSQL connection string
- engine: SQLAlchemy engine with connection pooling
- SessionLocal: Scoped session factory

---

### database/models/translation_record_model.py

**Purpose:**
SQLAlchemy ORM model for translation audit trail persistence.

**Classes:**

Class: TranslationRecordModel
Type: SQLAlchemy Model

Attributes:
- id: Integer (Primary Key)
- ticket_id: String(100) (Indexed)
- customer_id: Integer (Indexed)
- original_text: Text
- original_language: String(10) (Indexed)
- english_text: Text
- response_english: Text (Nullable)
- response_translated: Text (Nullable)
- response_language: String(10) (Indexed, Nullable)
- translation_service: String(50) (Default: "helsinki")
- translation_success: Boolean (Indexed, Default: True)
- created_at: DateTime (Server default: func.now(), Indexed)
- updated_at: DateTime (Server default & onupdate: func.now())

Purpose:
Stores all inbound and outbound translations with audit timestamps and success tracking.

---

### detection/script_detector.py

**Purpose:**
Layer 1 of language detection engine. Provides microsecond-speed script identification using Unicode ranges.

**Classes:**

Class: Scripts
Type: Constants

Values:
- DEVANAGARI = "devanagari"
- ARABIC = "arabic"
- CYRILLIC = "cyrillic"
- HANGUL = "hangul"
- CJK = "cjk"
- LATIN = "latin"
- UNKNOWN = "unknown"

Purpose:
Centralized script constants to prevent string typos.

Class: UnicodeRanges
Type: Constants

Purpose:
Named Unicode ranges for maintainability and scalability.

Class: ScriptDetector
Type: Service

Methods:
- `__init__()`
- `detect_script(text: str) -> str`

Purpose:
Scans text for non-Latin characters and returns script name (DEVANAGARI, ARABIC, CYRILLIC, HANGUL, CJK, LATIN, or UNKNOWN).

---

### detection/language_detector.py

**Purpose:**
Primary language classification engine. Orchestrates script detection, FastText, and LangDetect to form a consensus.

**Classes:**

Class: LanguageDetector
Type: Service

Methods:
- `__init__(fasttext_model_path: str = "models/lid.176.ftz")`
- `detect(text: str) -> DetectionResult`
- `_build_consensus(script: str, ft_lang: str, ft_conf: float, ld_lang: str, ld_conf: float, raw_results: dict) -> DetectionResult`
- `_detect_with_fasttext(text: str) -> Tuple[str, float]`
- `_detect_with_langdetect(text: str) -> Tuple[str, float]`

Purpose:
Orchestrates text-based ML detection with script fast-path optimization. Returns consensus DetectionResult.

**Dependencies:**
- fasttext module
- langdetect module
- ScriptDetector
- SCRIPT_LANGUAGE_MAP

---

### detection/detection_service.py

**Purpose:**
Facade for language detection layer. Orchestrates workflow between ML detection and CRM-based contextual resolution.

**Classes:**

Class: DetectionService
Type: Service/Facade

Methods:
- `__init__(fasttext_model_path: str = "models/lid.176.ftz")`
- `detect_language(text: str, customer_context: Optional[dict] = None) -> DetectionResult`

Purpose:
Sole public API boundary for detection layer. Coordinates text-based detection with context signal resolver.

**Dependencies:**
- LanguageDetector
- ContextSignalResolver

---

### detection/context_signal_resolver.py

**Purpose:**
Layer 3 customer intelligence. Rescues weak language detection signals using decoupled CRM context.

**Classes:**

Class: ContextSignalResolver
Type: Service

Methods:
- `__init__()`
- `resolve(text: str, detection_result: DetectionResult, customer_context: Optional[dict] = None) -> DetectionResult`
- `_should_apply_override(result: DetectionResult) -> bool`
- `_apply_preferred_language(result: DetectionResult, context: dict) -> Optional[DetectionResult]`
- `_apply_history_signal(result: DetectionResult, context: dict) -> Optional[DetectionResult]`
- `_apply_locale_signal(result: DetectionResult, context: dict) -> Optional[DetectionResult]`

Purpose:
Evaluates weak signals against customer context (preferred language, language history, locale) to upgrade confidence or override language detection.

**Constants:**
- STRONG_SIGNAL_THRESHOLD = 0.80
- SUPPORTED_LANGUAGES = {"en", "hi", "es", "fr", "de", "ar", "ko", "zh", "pt"}

---

### integrations/crm_translation_adapter.py

**Purpose:**
Placeholder file (currently empty).

---

### integrations/specialist_response_adapter.py

**Purpose:**
Converts Layer 2 specialist outputs into canonical TranslationRequest objects consumable by Layer 3.

**Classes:**

Class: SpecialistResponseAdapter
Type: Adapter

Methods:
- `__init__()`
- `adapt(output: Any, target_language: str) -> Optional[TranslationRequest]`
- `from_faq(output: FAQAgentOutput, target_language: str) -> Optional[TranslationRequest]`
- `from_refund(output: RefundOutput, target_language: str) -> Optional[TranslationRequest]`
- `from_account(output: AccountAgentResponse, target_language: str) -> Optional[TranslationRequest]`
- `from_proactive(output: ProactiveOutput, target_language: str) -> Optional[TranslationRequest]`
- `from_escalation(output: EscalationAgentResponse, target_language: str) -> Optional[TranslationRequest]`

Purpose:
Adapts outputs from multiple specialist agents (FAQ, Refund, Account, Proactive, Escalation) into unified TranslationRequest contracts.

**Consumes:**
- FAQAgentOutput
- RefundOutput
- AccountAgentResponse
- ProactiveOutput
- EscalationAgentResponse

**Produces:**
- TranslationRequest

---

### integrations/pre_layer0_translation_adapter.py

**Purpose:**
Orchestrates conversion between Layer 0 UnifiedTicket structures and Layer 3 translation engine boundaries.

**Classes:**

Class: Layer0TranslationAdapter
Type: Adapter

Methods:
- `__init__(translation_service: Any, translation_analytics: Optional[Any] = None, crm_repository: Optional[Any] = None)`
- `_get_customer_id(ticket_customer_id: str) -> Optional[int]`
- `_gather_customer_crm_data(customer_id: int) -> Dict[str, Any]`
- `_gather_language_context(customer_id: int, ticket_lang: str) -> Dict[str, Any]`
- `to_supervisor_payload(ticket: UnifiedTicket) -> Optional[Dict[str, Any]]`

Purpose:
Converts Layer 0 UnifiedTicket into supervisor payload with complete state context, CRM data, and language analytics.

**Consumes:**
- UnifiedTicket

**Produces:**
- Supervisor Payload (Dict)

---

### pipeline/inbound_translation_pipeline.py

**Purpose:**
Orchestrator for Layer 3 (Inbound). Converts raw customer messages in any language into safe, protected English for the Supervisor.

**Classes:**

Class: InboundTranslationPipeline
Type: Orchestrator

Methods:
- `__init__()`
- `process_inbound(text: str, customer_context: Optional[dict] = None) -> BilingualMessage`
- `_build_fast_path_message(text: str, lang: str, confidence: float, method: str) -> BilingualMessage`

Purpose:
10-step inbound workflow: detection → fast-path check → protection → caching → translation → validation → restoration → context building.

**Dependencies:**
- DetectionService
- FormatAndEntityProtector
- HelsinkiTranslator
- TranslationValidator
- TranslationCache

**Produces:**
- BilingualMessage

---

### pipeline/outbound_translation_pipeline.py

**Purpose:**
Orchestrator for Layer 3 (Outbound). Converts English responses back into customer's native language while protecting CRM variables.

**Classes:**

Class: OutboundTranslationPipeline
Type: Orchestrator

Methods:
- `__init__()`
- `process_outbound(english_response: str, target_language: str, source_agent: Optional[str] = None) -> TranslationResult`
- `_build_result(translated_text: str, target_language: str, success: bool, start_time: float) -> TranslationResult`

Purpose:
8-step outbound workflow: validation → language check → protection → caching → translation → validation → restoration → result building.

**Constants:**
- TRANSLATION_PROVIDER = "helsinki"
- SUPPORTED_OUTBOUND_LANGUAGES = {"hi", "es", "fr", "de", "ar"}

**Dependencies:**
- FormatAndEntityProtector
- HelsinkiTranslator
- TranslationValidator
- TranslationCache

**Produces:**
- TranslationResult

---

### protection/format_protector.py

**Purpose:**
Protects markdown and HTML format patterns from translation corruption.

**Classes:**

Class: FormatProtector
Type: Protection

Methods:
- `__init__()`
- `protect_formats(text: str) -> Tuple[str, Dict[str, str]]`
- `restore_formats(text: str, format_map: Dict[str, str]) -> str`

Purpose:
Replaces format patterns with placeholders before translation and restores them afterward.

**Constants:**
- PATTERNS: Dictionary of regex patterns for CODE_BLOCK, INLINE_CODE, LINK, BOLD, ITALIC, LIST, HTML

---

### protection/entity_extractor.py

**Purpose:**
Primary extraction engine. Identifies business-critical entities and normalizes IDs for consistent masking.

**Classes:**

Class: EntityExtractor
Type: Protection

Methods:
- `__init__()`
- `extract_entities(text: str) -> Dict[str, str]`

Purpose:
Scans text for ORDER_ID, TICKET_ID, CUSTOMER_ID, TRACKING_ID, EMAIL, PHONE, URL, AMOUNT and returns entity mapping.

**Constants:**
- SUPPORTED_ENTITY_TYPES: Set of recognized entity types
- ID_ENTITY_TYPES: Subset of entity types requiring uppercase normalization
- PATTERNS: Dictionary of regex patterns for each entity type

---

### protection/format_and_entity_protector.py

**Purpose:**
Facade for protection layer. Orchestrates format protection and entity masking with strict namespace separation.

**Classes:**

Class: FormatAndEntityProtector
Type: Facade

Methods:
- `__init__()`
- `protect(text: str) -> ProtectedContent`
- `restore(translated_text: str, content: ProtectedContent) -> str`

Purpose:
Coordinates entity extraction, placeholder creation, and format protection in sequence.

**Dependencies:**
- EntityExtractor
- PlaceholderManager
- FormatProtector

**Produces:**
- ProtectedContent

---

### protection/placeholder_manager.py

**Purpose:**
Manages transformation between sensitive entities and safe placeholders.

**Classes:**

Class: PlaceholderManager
Type: Protection

Methods:
- `__init__()`
- `create_placeholders(text: str, entities: Dict[str, str]) -> Tuple[str, Dict[str, str]]`
- `restore_placeholders(text: str, restoration_map: Dict[str, str]) -> str`

Purpose:
Converts extracted entities into placeholders (e.g., __EMAIL_1__) and provides restoration mapping for post-translation restoration.

---

### repositories/translation_repository.py

**Purpose:**
Data Access Object (DAO) for Layer 3 translation. Handles persistence, retrieval, and analytical queries.

**Classes:**

Class: TranslationRepository
Type: Repository

Methods:
- `__init__(db: Session)`
- `create_record(record: TranslationRecord) -> TranslationRecordModel`
- `get_by_ticket_id(ticket_id: str) -> Optional[TranslationRecordModel]`
- `update_outbound_translation(ticket_id: str, response_english: str, response_translated: str, response_language: str) -> bool`
- `update_translation_failure(ticket_id: str) -> bool`
- `translation_exists(ticket_id: str) -> bool`
- `get_customer_history(customer_id: int) -> List[TranslationRecordModel]`
- `get_by_customer_and_language(customer_id: int, language: str) -> List[TranslationRecordModel]`
- `get_failed_translations(limit: int = 100) -> List[TranslationRecordModel]`
- `get_recent_language_usage(days: int = 30) -> Dict[str, int]`

Purpose:
Manages all translation record CRUD operations, idempotency checks, and analytical queries.

**Database:**
- PostgreSQL

**Tables Referenced:**
- translation_records

---

### schemas/bilingual_message.py

**Purpose:**
Container for original and translated text with language context.

**Schemas:**

Schema: BilingualMessage

Fields:
- original_text: str
- english_text: str
- language_context: LanguageContext

Purpose:
Represents a message in two languages with comprehensive language detection and processing metadata.

---

### schemas/detection_result.py

**Purpose:**
Result object from language detection workflow.

**Schemas:**

Schema: DetectionResult

Fields:
- detected_language: str
- confidence: float
- detection_method: str
- script_detected: Optional[str]
- mixed_language_detected: bool
- raw_detector_results: Optional[dict]

Purpose:
Encapsulates language detection findings with confidence scores and detection methodology.

---

### schemas/language_context.py

**Purpose:**
Comprehensive language processing metadata.

**Schemas:**

Schema: LanguageContext

Fields:
- detected_language: str
- detection_confidence: float
- detection_method: str
- translation_used: bool
- translation_failed: bool
- fallback_triggered: bool
- mixed_language_detected: bool
- script_detected: Optional[str]
- original_message_stored: bool

Purpose:
Tracks language detection, translation decisions, and processing outcomes for a message.

---

### schemas/protected_content.py

**Purpose:**
Container for protected text and restoration mappings.

**Schemas:**

Schema: ProtectedContent

Fields:
- original_text: str
- protected_text: str
- entity_placeholders: Dict[str, str]
- format_placeholders: Dict[str, str]
- entity_count: int
- format_count: int

Purpose:
Represents text with entities and formats replaced by placeholders, storing mappings for restoration.

---

### schemas/translation_record.py

**Purpose:**
Domain model for translation persistence.

**Schemas:**

Schema: TranslationRecord

Fields:
- ticket_id: str
- customer_id: int
- original_text: str
- original_language: str
- english_text: str
- response_english: Optional[str]
- response_translated: Optional[str]
- response_language: Optional[str]
- translation_service: str
- translation_success: bool

Purpose:
Pydantic domain model enforcing architectural contracts for translation history storage.

---

### schemas/translation_result.py

**Purpose:**
Result from translation execution.

**Schemas:**

Schema: TranslationResult

Fields:
- translated_text: str
- source_language: str
- target_language: str
- translation_service: str
- translation_success: bool
- translation_confidence: Optional[float]

Purpose:
Contains translated output with service information and success/confidence metrics.

---

### schemas/translation_request.py

**Purpose:**
Canonical request contract from specialist agents to translation service.

**Schemas:**

Schema: TranslationRequest

Fields:
- ticket_id: str
- source_agent: str
- english_response: str
- target_language: str
- customer_id: Optional[int]

Purpose:
Unified representation of translation requests from any specialist agent.

---

### schemas/translation_persistence_event.py

**Purpose:**
Event wrapper for asynchronous translation persistence.

**Schemas:**

Schema: TranslationPersistenceEvent

Fields:
- event_id: str (default_factory: generate_event_id)
- ticket_id: str
- customer_id: int
- translation_record: TranslationRecord
- created_at: datetime (default_factory: generate_utc_now)
- source_system: str
- processing_status: str

Purpose:
Wraps translation records into audit events for async message broker dispatch.

---

### schemas/inbound_translation_response.py

**Purpose:**
Strict domain contract returned to Layer 1 Supervisor after inbound processing.

**Schemas:**

Schema: InboundTranslationResponse

Fields:
- bilingual_message: BilingualMessage
- translation_record: TranslationRecord
- persistence_event: TranslationPersistenceEvent

Purpose:
Complete response payload from inbound translation processing including bilingual content, persistence record, and event.

---

### service/translation_service.py

**Purpose:**
Master facade for Layer 3 translation subsystem. Orchestrates detection, protection, translation, and storage.

**Classes:**

Class: TranslationService
Type: Service/Facade

Methods:
- `__init__(repository: TranslationRepository)`
- `process_inbound_message(ticket_id: str, customer_id: int, message: str, customer_context: Optional[Dict[str, Any]] = None) -> InboundTranslationResponse`
- `process_outbound_response(ticket_id: str, english_response: str, target_language: str, source_agent: Optional[str] = None) -> TranslationResult`

Purpose:
Master orchestrator for complete translation workflows (inbound and outbound) with persistence and event generation.

**Dependencies:**
- TranslationRepository
- InboundTranslationPipeline
- OutboundTranslationPipeline
- BilingualStoreService
- TranslationPersistenceService
- TranslationAnalyticsService

**Consumes:**
- Raw customer messages
- Specialist agent responses

**Produces:**
- InboundTranslationResponse
- TranslationResult

---

### service/background_tasks.py

**Purpose:**
Coordinator for asynchronous/deferred operations. Ensures database writes and event dispatch do not block immediate responses.

**Classes:**

Class: BackgroundTasksService
Type: Service

Methods:
- `__init__(store_service: BilingualStoreService, persistence_service: TranslationPersistenceService)`
- `persist_inbound_translation(ticket_id: str, customer_id: int, bilingual_message: BilingualMessage) -> bool`
- `persist_outbound_translation(ticket_id: str, response_english: str, response_translated: str, response_language: str) -> bool`
- `dispatch_translation_event(event: TranslationPersistenceEvent) -> bool`

Purpose:
Deferred execution of persistence and event dispatch operations without blocking response returns.

**Dependencies:**
- BilingualStoreService
- TranslationPersistenceService

---

### storage/bilingual_store_service.py

**Purpose:**
Transforms and persists inbound translations. Acts as boundary between pipeline logic and data access.

**Classes:**

Class: BilingualStoreService
Type: Service

Methods:
- `__init__(repository: TranslationRepository)`
- `store_inbound_message(ticket_id: str, customer_id: int, bilingual_message: BilingualMessage) -> TranslationRecord`

Purpose:
Converts BilingualMessage into TranslationRecord and coordinates storage with idempotency checks.

**Dependencies:**
- TranslationRepository

**Consumes:**
- BilingualMessage

**Produces:**
- TranslationRecord

---

### storage/translation_persistence_service.py

**Purpose:**
Event coordinator and outbound persistence manager. Packages records into events and manages outbound database updates.

**Classes:**

Class: TranslationPersistenceService
Type: Service

Methods:
- `__init__(repository: TranslationRepository)`
- `create_persistence_event(translation_record: TranslationRecord, source_system: str = "inbound_pipeline") -> TranslationPersistenceEvent`
- `persist_outbound_translation(ticket_id: str, response_english: str, response_translated: str, response_language: str) -> bool`

Purpose:
Wraps records into audit events and manages outbound response persistence.

**Dependencies:**
- TranslationRepository

**Produces:**
- TranslationPersistenceEvent

---

### storage/translation_analytics_service.py

**Purpose:**
Transforms raw database metrics into business-friendly analytics. Enriched with observability logging and dominance scoring.

**Classes:**

Class: TranslationAnalyticsService
Type: Service

Methods:
- `__init__(repository: TranslationRepository)`
- `get_translation_health_metrics() -> Dict[str, Any]`
- `get_language_distribution(days: int = 30) -> Dict[str, Dict[str, float]]`
- `get_customer_language_profile(customer_id: int) -> Dict[str, Any]`

Purpose:
Calculates system health metrics, language usage distributions, and customer language preferences.

**Dependencies:**
- TranslationRepository

**Produces:**
- Health metrics (Dict)
- Language distribution (Dict)
- Customer profiles (Dict)

---

### tone/tone_adjustment_service.py

**Purpose:**
Applies agent-specific and language-specific tone adjustments before outbound translation.

**Classes:**

Class: ToneAdjustmentService
Type: Service

Methods:
- `__init__()`
- `adjust_tone(response_text: str, source_agent: str, target_language: str) -> str`
- `_build_prefix(agent_rule: Dict[str, Any], language_rule: Dict[str, Any]) -> str`
- `get_tone_metadata(source_agent: str, target_language: str) -> Dict[str, Any]`

Purpose:
Compounds multiple tone elements (apologies, empathy, formality) into prefix adjustments based on agent and language rules.

**Dependencies:**
- AGENT_TONE_RULES
- LANGUAGE_TONE_RULES

---

### tone/agent_tone_rules.py

**Purpose:**
Configuration mapping specialist agents to communication personas.

**Constants:**
- AGENT_TONE_RULES: Dictionary defining tone attributes for each agent:
  - faq_agent: helpful, neutral
  - refund_agent: professional, empathetic
  - account_agent: professional, neutral
  - technical_bug_agent: professional, empathetic, apologetic
  - escalation_agent: empathetic, formal, apologetic
  - proactive_agent: friendly, warm

---

### tone/language_tone_rules.py

**Purpose:**
Configuration mapping languages to cultural communication preferences.

**Constants:**
- LANGUAGE_TONE_RULES: Dictionary defining formality/style for each language:
  - en: neutral, direct
  - hi: respectful, professional
  - es: friendly, conversational
  - fr: formal, professional
  - de: formal, precise
  - ar: formal, respectful

---

### translation/helsinki_translator.py

**Purpose:**
Core translation engine. Orchestrates tokenization, model inference, and decoding using Helsinki-NLP.

**Classes:**

Class: HelsinkiTranslator
Type: Service

Methods:
- `__init__()`
- `translate(text: str, source_language: str, target_language: str = "en") -> TranslationResult`

Purpose:
Deterministic translation execution with guards against empty inputs and same-language bypasses.

**Dependencies:**
- ModelLoader
- transformers library (MarianMT)

**Produces:**
- TranslationResult

---

### translation/model_loader.py

**Purpose:**
Enterprise model manager. Ensures translation models load exactly once per language pair.

**Classes:**

Class: ModelLoader
Type: Manager

Methods:
- `__new__(cls)`
- `_initialize()`
- `is_loaded(source_language: str, target_language: str = "en") -> bool`
- `get_loaded_models() -> list[str]`
- `get_model(source_language: str, target_language: str = "en") -> tuple`

Purpose:
Singleton pattern implementation with thread-safe lazy loading of Helsinki-NLP models to prevent OOM errors.

**Constants:**
- SUPPORTED_MODELS: Dictionary of language pair to model identifier mappings:
  - Inbound pairs: (hi,en), (es,en), (fr,en), (de,en), (ar,en)
  - Outbound pairs: (en,hi), (en,es), (en,fr), (en,de), (en,ar)

**Type:**
Singleton/Manager

---

### translation/translation_cache.py

**Purpose:**
Thread-safe singleton translation cache. Prevents redundant neural network inference using SHA-256 hash keys.

**Classes:**

Class: TranslationCache
Type: Singleton/Cache

Methods:
- `__new__(cls)`
- `_initialize()`
- `_generate_key(text: str, source_language: str, target_language: str) -> str`
- `get(text: str, source_language: str, target_language: str = "en") -> Optional[TranslationResult]`
- `set(text: str, source_language: str, target_language: str, translation_result: TranslationResult) -> None`
- `clear() -> None`
- `size() -> int`

Purpose:
In-memory cache with thread-safe access to store and retrieve previously translated strings.

**Type:**
Singleton/Cache

---

### translation/translation_validator.py

**Purpose:**
Quality assurance for translation layer. Ensures LLM/Neural Network did not hallucinate or corrupt outputs.

**Classes:**

Class: TranslationValidator
Type: Validator

Methods:
- `__init__()`
- `validate(original_text: str, translated_text: str) -> bool`
- `_validate_empty_output(original_text: str, translated_text: str) -> bool`
- `_validate_placeholders(original_text: str, translated_text: str) -> bool`
- `_validate_length_drift(original_text: str, translated_text: str) -> bool`
- `_validate_minimum_content(original_text: str, translated_text: str) -> bool`

Purpose:
Executes validation sequence: empty output check → placeholder preservation → length drift detection → minimum content verification.

---

---

## Section 3: Folder Summary

### Folder Purpose

Demo3 is a comprehensive **Layer 3 Translation Subsystem** for a multi-lingual customer support platform. It orchestrates the complete lifecycle of customer message translation: detection, protection, translation, persistence, and analytics. The system supports bidirectional translation (customer language ↔ English) across multiple languages (Hindi, Spanish, French, German, Arabic) using Helsinki-NLP models. It integrates with Layer 0 (unified tickets), Layer 1 (supervisor), and Layer 2 (specialist agents) to provide safe, protected, cached translations with comprehensive audit trails and business KPIs.

### Files Included

**Analytics:** language_dashboard_service.py, language_metrics_service.py, materialized_view_manager.py

**Config:** setting.py, supported_languages.py, tone_configuration.py, translation_settings.py

**Database:** session.py, translation_record_model.py

**Detection:** context_signal_resolver.py, detection_service.py, language_detector.py, script_detector.py

**Integrations:** crm_translation_adapter.py, pre_layer0_translation_adapter.py, specialist_response_adapter.py

**Pipeline:** inbound_translation_pipeline.py, outbound_translation_pipeline.py

**Protection:** entity_extractor.py, format_and_entity_protector.py, format_protector.py, placeholder_manager.py

**Repositories:** translation_repository.py

**Schemas:** bilingual_message.py, detection_result.py, inbound_translation_response.py, language_context.py, protected_content.py, translation_persistence_event.py, translation_record.py, translation_request.py, translation_result.py

**Service:** background_tasks.py, translation_service.py

**Storage:** bilingual_store_service.py, translation_analytics_service.py, translation_persistence_service.py

**Tests:** 26 test files covering all modules

**Tone:** agent_tone_rules.py, language_tone_rules.py, tone_adjustment_service.py

**Translation:** helsinki_translator.py, model_loader.py, translation_cache.py, translation_validator.py

---

### Main Components

**Services:**
- TranslationService (master facade)
- DetectionService (language detection)
- InboundTranslationPipeline (customer message processing)
- OutboundTranslationPipeline (response translation)
- HelsinkiTranslator (core ML translation)
- LanguageDashboardService (analytics presentation)
- LanguageMetricsService (metrics aggregation)
- ToneAdjustmentService (communication tone)
- BackgroundTasksService (async operations)

**Repositories:**
- TranslationRepository (data access)

**Schemas/Models:**
- BilingualMessage
- DetectionResult
- LanguageContext
- ProtectedContent
- TranslationRecord
- TranslationResult
- TranslationRequest
- TranslationPersistenceEvent
- InboundTranslationResponse
- TranslationRecordModel (ORM)

**Protection:**
- FormatAndEntityProtector
- EntityExtractor
- PlaceholderManager
- FormatProtector

**Detection:**
- LanguageDetector
- ScriptDetector
- ContextSignalResolver

**Support:**
- ModelLoader (singleton pattern)
- TranslationCache (singleton pattern)
- TranslationValidator
- MaterializedViewManager
- SpecialistResponseAdapter
- Layer0TranslationAdapter

**Configuration:**
- Settings (database credentials)
- SCRIPT_LANGUAGE_MAP
- SUPPORTED_MODELS
- AGENT_TONE_RULES
- LANGUAGE_TONE_RULES

---

### Input / Output

**Input:**
- Customer messages in non-English languages (Hindi, Spanish, French, German, Arabic)
- Specialist agent responses in English
- Customer context (preferred language, language history, locale)
- UnifiedTicket structures from Layer 0

**Output:**
- BilingualMessage (original + translated with metadata)
- TranslationResult (translated text with service info)
- InboundTranslationResponse (complete inbound response)
- TranslationRecord (persistence model)
- Dashboard metrics and KPIs
- TranslationPersistenceEvent (audit events)
- Protected content mappings for safe transmission

---

## Critical Path & Dependencies

**Inbound Flow:**
DetectionService → InboundTranslationPipeline → BilingualStoreService → TranslationService → TranslationAnalyticsService

**Outbound Flow:**
SpecialistResponseAdapter → TranslationService → OutboundTranslationPipeline → ToneAdjustmentService

**Analytics Flow:**
TranslationRepository → TranslationAnalyticsService → LanguageMetricsService → LanguageDashboardService

**Detection Chain:**
ScriptDetector → LanguageDetector → ContextSignalResolver → DetectionResult

---

# Codebase Inventory & Documentation Report

## Section 1: Folder Structure

The structural layout of the `demo_analytic` project is outlined below:

```text
demo_analytic/
│
├── .gitignore
├── README.md
├── __init__.py
│
├── analytics/
│   ├── __init__.py
│   ├── agent_performance_service.py
│   ├── churn_analytics_service.py
│   ├── intent_analytics_service.py
│   ├── language_analytics_service.py
│   ├── roi_analytics_service.py
│   └── satisfaction_analytics_service.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── dashboard/
│   ├── __init__.py
│   └── dashboard_service.py
│
├── dispatchers/
│   ├── __init__.py
│   ├── email_dispatcher.py
│   └── slack_dispatcher.py
│
├── integrations/
│   ├── __init__.py
│   ├── customer_mapper.py
│   ├── feedback_mapper.py
│   ├── transcript_mapper.py
│   └── translation_mapper.py
│
├── materialized_views/
│   ├── __init__.py
│   ├── agent_performance_view.py
│   ├── customer_health_view.py
│   ├── intent_distribution_view.py
│   ├── language_metrics_view.py
│   ├── roi_metrics_view.py
│   └── view_manager.py
│
├── reports/
│   ├── __init__.py
│   ├── executive_summary_service.py
│   ├── knowledge_gap_report_service.py
│   └── roi_report_service.py
│
├── repositories/
│   ├── __init__.py
│   └── analytics_repository.py
│
├── schemas/
│   ├── __init__.py
│   ├── agent_metrics.py
│   ├── churn_metrics.py
│   ├── dashboard_snapshot.py
│   ├── intent_metrics.py
│   ├── knowledge_gap.py
│   ├── language_metrics.py
│   ├── roi_metrics.py
│   └── satisfaction_metrics.py
│
├── services/
│   ├── __init__.py
│   ├── churn_monitor_service.py
│   └── knowledge_gap_service.py
│
└── tests/
    ├── __init__.py
    ├── test_agent_performance_service.py
    ├── test_analytics_repository.py
    ├── test_churn_analytics_service.py
    ├── test_churn_monitor_service.py
    ├── test_dashboard_service.py
    ├── test_end_to_end_analytics_flow.py
    ├── test_intent_analytics_service.py
    ├── test_knowledge_gap_report_service.py
    ├── test_knowledge_gap_service.py
    ├── test_language_analytics_service.py
    ├── test_roi_analytics_service.py
    ├── test_roi_report_service.py
    └── test_satisfaction_analytics_service.py
```

---

## Section 2: File Analysis

### File: [demo_analytic/analytics/agent_performance_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/agent_performance_service.py)
#### Purpose
Computes Layer 2 specialist agent operational and velocity KPIs from transcript data.

#### Classes
* **Class**: [AgentPerformanceAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/agent_performance_service.py#L9)
  * **Type**: Service
  * **Methods**:
    - `calculate_agent_metrics()`
  * **Purpose**: Groups transcript events by agent and computes volumetric rates, speeds, and outcomes.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [AgentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py#L8) (Schema)
* **Produces**:
  - [AgentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py#L8) (List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/analytics/churn_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/churn_analytics_service.py)
#### Purpose
Predictive engine calculating customer risk scores, classifications, and triggers.

#### Classes
* **Class**: [ChurnAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/churn_analytics_service.py#L8)
  * **Type**: Service
  * **Methods**:
    - `calculate_churn_metrics()`
  * **Purpose**: Processes customer records to determine risk tiers and drivers.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `LOW_RISK_MAX`
* `MEDIUM_RISK_MAX`
* `SENTIMENT_THRESHOLD`
* `UNRESOLVED_TICKETS_THRESHOLD`
* `INACTIVITY_THRESHOLD_DAYS`

#### Relationships
* **Consumes**:
  - [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18) (Schema)
* **Produces**:
  - [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18) (List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/analytics/intent_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/intent_analytics_service.py)
#### Purpose
Orchestrates volumetric allocations and growth metrics for routing intents.

#### Classes
* **Class**: [IntentAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/intent_analytics_service.py#L9)
  * **Type**: Service
  * **Methods**:
    - `calculate_intent_metrics()`
  * **Purpose**: Computes ticket volumes and growth indicators grouped by intent.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `KNOWN_INTENTS`

#### Relationships
* **Consumes**:
  - [IntentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L11) (Schema)
* **Produces**:
  - [IntentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L11) (List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/analytics/language_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/language_analytics_service.py)
#### Purpose
Computes adoption metrics and translation success counts per language.

#### Classes
* **Class**: [LanguageAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/language_analytics_service.py#L9)
  * **Type**: Service
  * **Methods**:
    - `calculate_language_metrics()`
  * **Purpose**: Compiles language usage statistics and translation success rates.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `CANONICAL_LANGUAGE_NAMES`

#### Relationships
* **Consumes**:
  - [LanguageMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L20) (Schema)
* **Produces**:
  - [LanguageMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L20) (List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/analytics/roi_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/roi_analytics_service.py)
#### Purpose
Calculates gross and net automation savings and technology investment ratios.

#### Classes
* **Class**: [ROIAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/roi_analytics_service.py#L9)
  * **Type**: Service
  * **Methods**:
    - `calculate_roi_metrics()`
  * **Purpose**: Computes ROI percentage and net operational savings for customer accounts.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8) (Schema)
* **Produces**:
  - [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/analytics/satisfaction_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/satisfaction_analytics_service.py)
#### Purpose
Calculates customer satisfaction score distributions and POP trend metrics.

#### Classes
* **Class**: [SatisfactionAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/satisfaction_analytics_service.py#L9)
  * **Type**: Service
  * **Methods**:
    - `_calculate_distribution_and_rate()`
    - `calculate_satisfaction_metrics()`
  * **Purpose**: Derives CSAT values and trend rates across reporting intervals.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [SatisfactionMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py#L7) (Schema)
* **Produces**:
  - [SatisfactionMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py#L7)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/config/settings.py](file:///d:/CRM%20agent/demo_analytic/config/settings.py)
#### Purpose
Configures database connectivity, SMTP, LLM, and Slack details from environment variables.

#### Classes
* **Class**: [Settings](file:///d:/CRM%20agent/demo_analytic/config/settings.py#L4)
  * **Type**: Utility
  * **Methods**: None
  * **Purpose**: Holds system configuration parameters and manages `.env` validation.

#### Schemas / Models
* **Schema**: [Settings](file:///d:/CRM%20agent/demo_analytic/config/settings.py#L4)
  * **Fields**:
    - `db_user` : `str`
    - `db_pass` : `str`
    - `db_host` : `str`
    - `db_port` : `int`
    - `db_name` : `str`
    - `SMTP_PASSWORD` : `str`
    - `SMTP_SERVER` : `str`
    - `SMTP_PORT` : `int`
    - `SMTP_SENDER` : `str`
    - `GROQ_API_KEY` : `str`
    - `LANGCHAIN_API_KEY` : `str`
    - `LANGCHAIN_TRACING_V2` : `bool`
    - `LANGCHAIN_PROJECT` : `str`
    - `SLACK_WEBHOOK_URL` : `str`
  * **Purpose**: Root validation schema for application environment parameters.

#### Enums
None

#### Functions
None

#### Constants
* `settings` (Instance of Settings)

#### Relationships
* **Used By**:
  - [EmailDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/email_dispatcher.py#L12)
  - [SlackDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/slack_dispatcher.py#L9)

---

### File: [demo_analytic/dashboard/dashboard_service.py](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py)
#### Purpose
Master orchestration service coordinating data extraction, mapping, and metric assembly.

#### Classes
* **Class**: [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)
  * **Type**: Service
  * **Methods**:
    - `__init__()`
    - `generate_dashboard_snapshot()`
  * **Purpose**: Aggregates distinct metrics to formulate a complete system state snapshot.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [AnalyticsRepository](file:///d:/CRM%20agent/demo_analytic/repositories/analytics_repository.py#L9)
  - [TranscriptMapper](file:///d:/CRM%20agent/demo_analytic/integrations/transcript_mapper.py#L6)
  - [FeedbackMapper](file:///d:/CRM%20agent/demo_analytic/integrations/feedback_mapper.py#L5)
  - [TranslationMapper](file:///d:/CRM%20agent/demo_analytic/integrations/translation_mapper.py#L6)
  - [CustomerMapper](file:///d:/CRM%20agent/demo_analytic/integrations/customer_mapper.py#L5)
* **Produces**:
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/dispatchers/email_dispatcher.py](file:///d:/CRM%20agent/demo_analytic/dispatchers/email_dispatcher.py)
#### Purpose
SMTP infrastructure adapter transmitting structured summaries to emails.

#### Classes
* **Class**: [EmailDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/email_dispatcher.py#L12)
  * **Type**: Dispatcher
  * **Methods**:
    - `__init__()`
    - `_send_email()`
    - `send_roi_report()`
    - `send_knowledge_gap_report()`
    - `send_executive_summary()`
  * **Purpose**: Constructs MIME messages and routes email data.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [Settings](file:///d:/CRM%20agent/demo_analytic/config/settings.py#L4)

---

### File: [demo_analytic/dispatchers/slack_dispatcher.py](file:///d:/CRM%20agent/demo_analytic/dispatchers/slack_dispatcher.py)
#### Purpose
Webhook infrastructure adapter pushing notifications to Slack channels.

#### Classes
* **Class**: [SlackDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/slack_dispatcher.py#L9)
  * **Type**: Dispatcher
  * **Methods**:
    - `__init__()`
    - `_send_message()`
    - `send_churn_alert()`
    - `send_knowledge_gap_summary()`
    - `send_executive_summary()`
  * **Purpose**: Executes HTTP requests containing markdown blocks to external webhooks.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [Settings](file:///d:/CRM%20agent/demo_analytic/config/settings.py#L4)

---

### File: [demo_analytic/integrations/customer_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/customer_mapper.py)
#### Purpose
ACL mapper normalizing customer database dictionaries to analytics structures.

#### Classes
* **Class**: [CustomerMapper](file:///d:/CRM%20agent/demo_analytic/integrations/customer_mapper.py#L5)
  * **Type**: Mapper
  * **Methods**:
    - `map_customer_row()`
    - `map_customer_rows()`
  * **Purpose**: Safely handles missing data and casts CRM identifiers.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/integrations/feedback_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/feedback_mapper.py)
#### Purpose
ACL mapper formatting customer sentiment and question records.

#### Classes
* **Class**: [FeedbackMapper](file:///d:/CRM%20agent/demo_analytic/integrations/feedback_mapper.py#L5)
  * **Type**: Mapper
  * **Methods**:
    - `map_feedback_row()`
    - `map_feedback_rows()`
  * **Purpose**: Categorizes sentiment tags to positive, negative, or neutral.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `UNKNOWN_FEEDBACK`
* `UNKNOWN_TOPIC`

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/integrations/transcript_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/transcript_mapper.py)
#### Purpose
ACL mapper structuring ticket log parameters for agent and ROI services.

#### Classes
* **Class**: [TranscriptMapper](file:///d:/CRM%20agent/demo_analytic/integrations/transcript_mapper.py#L6)
  * **Type**: Mapper
  * **Methods**:
    - `map_agent_row()`
    - `map_agent_rows()`
    - `map_intent_row()`
    - `map_intent_rows()`
    - `map_roi_row()`
    - `map_roi_rows()`
    - `map_feedback_row()`
    - `map_feedback_rows()`
  * **Purpose**: Converts time intervals and normalizes agent outcome tags.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/integrations/translation_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/translation_mapper.py)
#### Purpose
ACL mapper synchronizing translation success flags and language structures.

#### Classes
* **Class**: [TranslationMapper](file:///d:/CRM%20agent/demo_analytic/integrations/translation_mapper.py#L6)
  * **Type**: Mapper
  * **Methods**:
    - `map_translation_row()`
    - `map_translation_rows()`
  * **Purpose**: Checks string representations of truth and maps ISO languages.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `UNKNOWN_LANGUAGE`
* `TRUE_VALUES`
* `FALSE_VALUES`

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/materialized_views/agent_performance_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/agent_performance_view.py)
#### Purpose
Defines sql statements generating daily pre-aggregated agent metrics.

#### Classes
None

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `VIEW_NAME`
* `CREATE_VIEW_SQL`
* `CREATE_INDEX_SQL`
* `DROP_VIEW_SQL`
* `REFRESH_VIEW_SQL`

#### Relationships
* **Used By**:
  - [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

---

### File: [demo_analytic/materialized_views/customer_health_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/customer_health_view.py)
#### Purpose
Defines sql statements pre-computing churn risk contexts.

#### Classes
None

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `VIEW_NAME`
* `CREATE_VIEW_SQL`
* `CREATE_INDEX_SQL`
* `DROP_VIEW_SQL`
* `REFRESH_VIEW_SQL`

#### Relationships
* **Used By**:
  - [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

---

### File: [demo_analytic/materialized_views/intent_distribution_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/intent_distribution_view.py)
#### Purpose
Defines sql statements pre-aggregating day-by-day intent allocations.

#### Classes
None

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `VIEW_NAME`
* `CREATE_VIEW_SQL`
* `CREATE_INDEX_SQL`
* `DROP_VIEW_SQL`
* `REFRESH_VIEW_SQL`

#### Relationships
* **Used By**:
  - [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

---

### File: [demo_analytic/materialized_views/language_metrics_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/language_metrics_view.py)
#### Purpose
Defines sql statements pre-aggregating day-by-day translation metrics.

#### Classes
None

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `VIEW_NAME`
* `CREATE_VIEW_SQL`
* `CREATE_INDEX_SQL`
* `DROP_VIEW_SQL`
* `REFRESH_VIEW_SQL`

#### Relationships
* **Used By**:
  - [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

---

### File: [demo_analytic/materialized_views/roi_metrics_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/roi_metrics_view.py)
#### Purpose
Defines sql statements pre-aggregating customer financial counts.

#### Classes
None

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `VIEW_NAME`
* `CREATE_VIEW_SQL`
* `CREATE_INDEX_SQL`
* `DROP_VIEW_SQL`
* `REFRESH_VIEW_SQL`

#### Relationships
* **Used By**:
  - [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

---

### File: [demo_analytic/materialized_views/view_manager.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py)
#### Purpose
Coordinates database initialization, index execution, and refreshes for OLAP views.

#### Classes
* **Class**: [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)
  * **Type**: View/Manager
  * **Methods**:
    - `__init__()`
    - `initialize_all_views()`
    - `refresh_all_views()`
    - `drop_all_views()`
  * **Purpose**: Orchestrates database lifecycle operations for materialized views.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [agent_performance_view](file:///d:/CRM%20agent/demo_analytic/materialized_views/agent_performance_view.py)
  - [intent_distribution_view](file:///d:/CRM%20agent/demo_analytic/materialized_views/intent_distribution_view.py)
  - [customer_health_view](file:///d:/CRM%20agent/demo_analytic/materialized_views/customer_health_view.py)
  - [language_metrics_view](file:///d:/CRM%20agent/demo_analytic/materialized_views/language_metrics_view.py)
  - [roi_metrics_view](file:///d:/CRM%20agent/demo_analytic/materialized_views/roi_metrics_view.py)

---

### File: [demo_analytic/reports/executive_summary_service.py](file:///d:/CRM%20agent/demo_analytic/reports/executive_summary_service.py)
#### Purpose
Distills comprehensive snapshots to formatted executive plain-text summaries.

#### Classes
* **Class**: [ExecutiveSummaryService](file:///d:/CRM%20agent/demo_analytic/reports/executive_summary_service.py#L7)
  * **Type**: Service
  * **Methods**:
    - `generate_summary()`
  * **Purpose**: Assembles multi-area metric strings for dispatch channels.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `AGENT_DISPLAY_NAMES`

#### Relationships
* **Consumes**:
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16) (Schema)

---

### File: [demo_analytic/reports/knowledge_gap_report_service.py](file:///d:/CRM%20agent/demo_analytic/reports/knowledge_gap_report_service.py)
#### Purpose
Formats identified document gaps into text summaries grouped by severity.

#### Classes
* **Class**: [KnowledgeGapReportService](file:///d:/CRM%20agent/demo_analytic/reports/knowledge_gap_report_service.py#L5)
  * **Type**: Service
  * **Methods**:
    - `generate_report()`
  * **Purpose**: Formats topics, satisfaction indexes, and example questions.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [KnowledgeGap](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L20) (Schema List)

---

### File: [demo_analytic/reports/roi_report_service.py](file:///d:/CRM%20agent/demo_analytic/reports/roi_report_service.py)
#### Purpose
Formats computed client ROI parameters into presentation summaries.

#### Classes
* **Class**: [ROIReportService](file:///d:/CRM%20agent/demo_analytic/reports/roi_report_service.py#L6)
  * **Type**: Service
  * **Methods**:
    - `generate_report()`
  * **Purpose**: Generates automation, net financial savings, and efficiency descriptions.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Consumes**:
  - [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8) (Schema)

---

### File: [demo_analytic/repositories/analytics_repository.py](file:///d:/CRM%20agent/demo_analytic/repositories/analytics_repository.py)
#### Purpose
DAO containing raw SQL structures mapping to relational support logs.

#### Classes
* **Class**: [AnalyticsRepository](file:///d:/CRM%20agent/demo_analytic/repositories/analytics_repository.py#L9)
  * **Type**: Repository
  * **Methods**:
    - `__init__()`
    - `get_platform_summary()`
    - `get_agent_data()`
    - `get_intent_data()`
    - `get_feedback_data()`
    - `get_language_data()`
    - `get_all_customer_churn_data()`
    - `get_customer_churn_data()`
    - `get_roi_data()`
  * **Purpose**: Executes query blocks on database connection sessions.

#### Special Rules
* **Database**: PostgreSQL
* **Tables Referenced**:
  - `ticket_transcripts`
  - `translation_records`
  - `customers`

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/schemas/agent_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py)
#### Purpose
Pydantic schema structure detailing KPIs for individual support agents.

#### Classes
* **Class**: [AgentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py#L8)
  * **Type**: Pydantic Model
  * **Methods**:
    - `unresolved_count` (property)
    - `validate_volumetric_integrity()`
  * **Purpose**: Validates handled counts and outcome ratios.

#### Schemas / Models
* **Schema**: [AgentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py#L8)
  * **Fields**:
    - `agent_name` : `str`
    - `tickets_handled` : `int`
    - `resolved_count` : `int`
    - `escalated_count` : `int`
    - `resolution_rate` : `float`
    - `escalation_rate` : `float`
    - `avg_resolution_time_seconds` : `float`
    - `satisfaction_rate` : `float`
    - `period_start` : `datetime`
    - `period_end` : `datetime`
  * **Purpose**: Defines agent volume, time, CSAT, and window trackers.

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [AgentPerformanceAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/agent_performance_service.py#L9)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/churn_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py)
#### Purpose
Pydantic schema structure mapping client churn factors.

#### Classes
* **Class**: [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_risk_classification_consistency()`
  * **Purpose**: Validates risk category parameters against numeric values.

#### Schemas / Models
* **Schema**: [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18)
  * **Fields**:
    - `customer_id` : `Union[str, int]`
    - `customer_name` : `str`
    - `risk_score` : `float`
    - `risk_level` : `ChurnRiskTier`
    - `risk_drivers` : `list[RiskDriverType]`
    - `last_sentiment_score` : `float`
    - `unresolved_ticket_count` : `int`
    - `days_since_last_activity` : `int`
    - `computed_at` : `datetime`
  * **Purpose**: Compiles a single tenant's risk attributes.

#### Enums
* **Enum**: [ChurnRiskTier](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L7)
  * **Values**:
    - `LOW`
    - `MEDIUM`
    - `HIGH`
  * **Purpose**: Customer churn probability categories.
* **Enum**: [RiskDriverType](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L9)
  * **Values**:
    - `negative_sentiment`
    - `unresolved_tickets`
    - `customer_inactivity`
    - `high_escalation_rate`
    - `declining_usage`
  * **Purpose**: Identifiers mapping reasons for elevated churn probability.

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [ChurnAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/churn_analytics_service.py#L8)
  - [ChurnMonitorService](file:///d:/CRM%20agent/demo_analytic/services/churn_monitor_service.py#L7)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/dashboard_snapshot.py](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py)
#### Purpose
Pydantic envelope schema packing the completed analytical state metrics.

#### Classes
* **Class**: [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_snapshot_and_temporal_alignment()`
  * **Purpose**: Asserts that internal schema intervals match root bounds.

#### Schemas / Models
* **Schema**: [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)
  * **Fields**:
    - `snapshot_id` : `str`
    - `generated_at` : `datetime`
    - `report_period_start` : `datetime`
    - `report_period_end` : `datetime`
    - `total_tickets` : `int`
    - `total_customers` : `int`
    - `agent_metrics` : `list[AgentMetrics]`
    - `intent_metrics` : `list[IntentMetrics]`
    - `satisfaction_metrics` : `SatisfactionMetrics`
    - `roi_metrics` : `ROIMetrics`
    - `language_metrics` : `list[LanguageMetrics]`
    - `high_risk_customers` : `list[ChurnMetrics]`
    - `knowledge_gaps` : `list[KnowledgeGap]`
  * **Purpose**: Formulates the master structure delivering all analytics components.

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)
  - [ExecutiveSummaryService](file:///d:/CRM%20agent/demo_analytic/reports/executive_summary_service.py#L7)

---

### File: [demo_analytic/schemas/intent_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py)
#### Purpose
Pydantic schema mapping allocations and growths per intent.

#### Classes
* **Class**: [IntentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L11)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_mathematical_integrity()`
  * **Purpose**: Compares current values against historical targets to check growth ratios.

#### Schemas / Models
* **Schema**: [IntentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L11)
  * **Fields**:
    - `intent_name` : `Layer1IntentType`
    - `ticket_count` : `int`
    - `percentage` : `float`
    - `previous_period_count` : `int`
    - `growth_rate` : `Optional[float]`
    - `period_start` : `datetime`
    - `period_end` : `datetime`
  * **Purpose**: Represents details for a single intent classification.

#### Enums
* **Enum**: [Layer1IntentType](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L8)
  * **Values**:
    - `faq`
    - `refund_request`
    - `account_issue`
    - `technical_bug`
    - `angry_complex`
  * **Purpose**: Allowed categorization classes handled at Level 1 routing.

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [IntentAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/intent_analytics_service.py#L9)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/knowledge_gap.py](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py)
#### Purpose
Pydantic schema mapping semantically clustered documentation issues.

#### Classes
* **Class**: [KnowledgeGap](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L20)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_intelligence_and_temporal_integrity()`
  * **Purpose**: Verifies that severity categories match cluster metrics.

#### Schemas / Models
* **Schema**: [KnowledgeGap](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L20)
  * **Fields**:
    - `cluster_id` : `str`
    - `topic` : `str`
    - `occurrences` : `int`
    - `severity` : `GapSeverityTier`
    - `satisfaction_rate` : `float`
    - `sample_questions` : `list[str]`
    - `suggested_article_title` : `str`
    - `suggested_action` : `GapActionType`
    - `detected_at` : `datetime`
  * **Purpose**: Contains topics, customer questions, and recommended updates.

#### Enums
* **Enum**: [GapSeverityTier](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L8)
  * **Values**:
    - `LOW`
    - `MEDIUM`
    - `HIGH`
  * **Purpose**: Urgency identifiers for gaps.
* **Enum**: [GapActionType](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L11)
  * **Values**:
    - `CREATE_FAQ_ARTICLE`
    - `UPDATE_EXISTING_ARTICLE`
    - `ADD_PRODUCT_DOCUMENTATION`
    - `IMPROVE_WORKFLOW`
    - `ESCALATE_TO_PRODUCT_TEAM`
  * **Purpose**: Formats standard recommended remediation steps.

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [KnowledgeGapService](file:///d:/CRM%20agent/demo_analytic/services/knowledge_gap_service.py#L7)
  - [KnowledgeGapReportService](file:///d:/CRM%20agent/demo_analytic/reports/knowledge_gap_report_service.py#L5)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/language_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py)
#### Purpose
Pydantic schema detailing adoption and translation success counts.

#### Classes
* **Class**: [LanguageMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L20)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_language_mathematical_and_temporal_integrity()`
  * **Purpose**: Validates ISO identifiers and growth rates.

#### Schemas / Models
* **Schema**: [LanguageMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L20)
  * **Fields**:
    - `language_code` : `SupportedISOLanguages`
    - `language_name` : `str`
    - `ticket_count` : `int`
    - `satisfaction_rate` : `float`
    - `translation_success_rate` : `float`
    - `previous_period_count` : `int`
    - `growth_rate` : `Optional[float]`
    - `period_start` : `datetime`
    - `period_end` : `datetime`
  * **Purpose**: Maps transaction volumes and translation success counts.

#### Enums
* **Enum**: [SupportedISOLanguages](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L8)
  * **Values**:
    - `en`
    - `hi`
    - `es`
    - `fr`
    - `de`
    - `ar`
  * **Purpose**: List of standard language identifiers supported by translation models.

#### Functions
None

#### Constants
* `CANONICAL_LANGUAGE_NAMES`

#### Relationships
* **Used By**:
  - [LanguageAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/language_analytics_service.py#L9)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/roi_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py)
#### Purpose
Pydantic schema detailing financial net outcomes and automation rates.

#### Classes
* **Class**: [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_financial_and_volumetric_integrity()`
  * **Purpose**: Checks the alignment of automation rates, gross, and net values.

#### Schemas / Models
* **Schema**: [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8)
  * **Fields**:
    - `customer_id` : `Union[str, int]`
    - `customer_name` : `str`
    - `total_tickets` : `int`
    - `auto_resolved_tickets` : `int`
    - `escalated_tickets` : `int`
    - `auto_resolution_rate` : `float`
    - `estimated_cost_per_ticket` : `float`
    - `gross_savings` : `float`
    - `platform_cost` : `float`
    - `net_savings` : `float`
    - `roi_percentage` : `Optional[float]`
    - `period_start` : `datetime`
    - `period_end` : `datetime`
  * **Purpose**: Maps operational variables to savings.

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [ROIAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/roi_analytics_service.py#L9)
  - [ROIReportService](file:///d:/CRM%20agent/demo_analytic/reports/roi_report_service.py#L6)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/schemas/satisfaction_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py)
#### Purpose
Pydantic schema tracking customer satisfaction rates and POP changes.

#### Classes
* **Class**: [SatisfactionMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py#L7)
  * **Type**: Pydantic Model
  * **Methods**:
    - `validate_satisfaction_mathematical_integrity()`
  * **Purpose**: Asserts feedback sum totals and verifies CSAT rates match positive weights.

#### Schemas / Models
* **Schema**: [SatisfactionMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py#L7)
  * **Fields**:
    - `positive_feedback_count` : `int`
    - `negative_feedback_count` : `int`
    - `neutral_feedback_count` : `int`
    - `total_feedback_count` : `int`
    - `satisfaction_rate` : `float`
    - `previous_period_rate` : `float`
    - `trend_percentage` : `float`
    - `period_start` : `datetime`
    - `period_end` : `datetime`
  * **Purpose**: Normalizes customer surveys to metrics.

#### Enums
None

#### Functions
None

#### Constants
None

#### Relationships
* **Used By**:
  - [SatisfactionAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/satisfaction_analytics_service.py#L9)
  - [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)

---

### File: [demo_analytic/services/churn_monitor_service.py](file:///d:/CRM%20agent/demo_analytic/services/churn_monitor_service.py)
#### Purpose
Filters and aggregates calculated client risk metrics for customer success.

#### Classes
* **Class**: [ChurnMonitorService](file:///d:/CRM%20agent/demo_analytic/services/churn_monitor_service.py#L7)
  * **Type**: Service
  * **Methods**:
    - `get_high_risk_customers()`
    - `get_top_n_risks()`
    - `summarize_risk_distribution()`
  * **Purpose**: Identifies high risk accounts and aggregates distribution.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `DEFAULT_HIGH_RISK_THRESHOLD`

#### Relationships
* **Consumes**:
  - [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18) (Schema List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### File: [demo_analytic/services/knowledge_gap_service.py](file:///d:/CRM%20agent/demo_analytic/services/knowledge_gap_service.py)
#### Purpose
Groups raw customer questions to compute documentation issues.

#### Classes
* **Class**: [KnowledgeGapService](file:///d:/CRM%20agent/demo_analytic/services/knowledge_gap_service.py#L7)
  * **Type**: Service
  * **Methods**:
    - `calculate_knowledge_gaps()`
  * **Purpose**: Compiles topics, frequency counters, and recommended actions.

#### Schemas / Models
None

#### Enums
None

#### Functions
None

#### Constants
* `HIGH_SEVERITY_MIN`
* `MEDIUM_SEVERITY_MIN`
* `SUGGESTED_TITLES`

#### Relationships
* **Consumes**:
  - [KnowledgeGap](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L20) (Schema List)
* **Used By**:
  - [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)

---

### System Initialization and Configuration Placeholders
The project contains standard placeholders, environment exclusions, and empty test package initializers. None of these files contain logical definitions, classes, functions, or constants:

* **File**: `demo_analytic/.gitignore` (Purpose: Git version control exclusion patterns)
* **File**: `demo_analytic/README.md` (Purpose: Project documentation placeholder)
* **File**: `demo_analytic/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/analytics/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/config/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/dashboard/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/dispatchers/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/integrations/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/materialized_views/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/reports/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/repositories/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/schemas/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/services/__init__.py` (Purpose: Package initialisation helper)
* **File**: `demo_analytic/tests/__init__.py` (Purpose: Test package initialization)
* **File**: `demo_analytic/tests/test_agent_performance_service.py` (Purpose: Agent analytics unit tests)
* **File**: `demo_analytic/tests/test_analytics_repository.py` (Purpose: SQL repository unit tests)
* **File**: `demo_analytic/tests/test_churn_analytics_service.py` (Purpose: Churn analytics unit tests)
* **File**: `demo_analytic/tests/test_churn_monitor_service.py` (Purpose: Churn monitor service unit tests)
* **File**: `demo_analytic/tests/test_dashboard_service.py` (Purpose: Snapshot service unit tests)
* **File**: `demo_analytic/tests/test_end_to_end_analytics_flow.py` (Purpose: Integrated pipeline tests)
* **File**: `demo_analytic/tests/test_intent_analytics_service.py` (Purpose: Level 1 intent routing unit tests)
* **File**: `demo_analytic/tests/test_knowledge_gap_report_service.py` (Purpose: Gap report generation unit tests)
* **File**: `demo_analytic/tests/test_knowledge_gap_service.py` (Purpose: Semantic gap identification unit tests)
* **File**: `demo_analytic/tests/test_language_analytics_service.py` (Purpose: Language adoption unit tests)
* **File**: `demo_analytic/tests/test_roi_analytics_service.py` (Purpose: ROI commercial calculations unit tests)
* **File**: `demo_analytic/tests/test_roi_report_service.py` (Purpose: Financial report formatting unit tests)
* **File**: `demo_analytic/tests/test_satisfaction_analytics_service.py` (Purpose: CSAT trend analysis unit tests)

---

## Section 3: Folder Summary

### Folder Purpose
The `demo_analytic` folder forms the complete codebase repository for a multi-tenant business intelligence pipeline. It manages SQL-level database access via OLAP materialized views and repositories, parses database items through Anti-Corruption Layer (ACL) mappers, processes metrics via specialized analytics services, models results into strict Pydantic schemas, builds reports, and delivers alert emails/slack messages.

### Files Included
All files included in the project are:
* [demo_analytic/analytics/__init__.py](file:///d:/CRM%20agent/demo_analytic/analytics/__init__.py)
* [demo_analytic/analytics/agent_performance_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/agent_performance_service.py)
* [demo_analytic/analytics/churn_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/churn_analytics_service.py)
* [demo_analytic/analytics/intent_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/intent_analytics_service.py)
* [demo_analytic/analytics/language_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/language_analytics_service.py)
* [demo_analytic/analytics/roi_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/roi_analytics_service.py)
* [demo_analytic/analytics/satisfaction_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/analytics/satisfaction_analytics_service.py)
* [demo_analytic/config/__init__.py](file:///d:/CRM%20agent/demo_analytic/config/__init__.py)
* [demo_analytic/config/settings.py](file:///d:/CRM%20agent/demo_analytic/config/settings.py)
* [demo_analytic/dashboard/__init__.py](file:///d:/CRM%20agent/demo_analytic/dashboard/__init__.py)
* [demo_analytic/dashboard/dashboard_service.py](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py)
* [demo_analytic/dispatchers/__init__.py](file:///d:/CRM%20agent/demo_analytic/dispatchers/__init__.py)
* [demo_analytic/dispatchers/email_dispatcher.py](file:///d:/CRM%20agent/demo_analytic/dispatchers/email_dispatcher.py)
* [demo_analytic/dispatchers/slack_dispatcher.py](file:///d:/CRM%20agent/demo_analytic/dispatchers/slack_dispatcher.py)
* [demo_analytic/integrations/__init__.py](file:///d:/CRM%20agent/demo_analytic/integrations/__init__.py)
* [demo_analytic/integrations/customer_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/customer_mapper.py)
* [demo_analytic/integrations/feedback_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/feedback_mapper.py)
* [demo_analytic/integrations/transcript_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/transcript_mapper.py)
* [demo_analytic/integrations/translation_mapper.py](file:///d:/CRM%20agent/demo_analytic/integrations/translation_mapper.py)
* [demo_analytic/materialized_views/__init__.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/__init__.py)
* [demo_analytic/materialized_views/agent_performance_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/agent_performance_view.py)
* [demo_analytic/materialized_views/customer_health_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/customer_health_view.py)
* [demo_analytic/materialized_views/intent_distribution_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/intent_distribution_view.py)
* [demo_analytic/materialized_views/language_metrics_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/language_metrics_view.py)
* [demo_analytic/materialized_views/roi_metrics_view.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/roi_metrics_view.py)
* [demo_analytic/materialized_views/view_manager.py](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py)
* [demo_analytic/reports/__init__.py](file:///d:/CRM%20agent/demo_analytic/reports/__init__.py)
* [demo_analytic/reports/executive_summary_service.py](file:///d:/CRM%20agent/demo_analytic/reports/executive_summary_service.py)
* [demo_analytic/reports/knowledge_gap_report_service.py](file:///d:/CRM%20agent/demo_analytic/reports/knowledge_gap_report_service.py)
* [demo_analytic/reports/roi_report_service.py](file:///d:/CRM%20agent/demo_analytic/reports/roi_report_service.py)
* [demo_analytic/repositories/__init__.py](file:///d:/CRM%20agent/demo_analytic/repositories/__init__.py)
* [demo_analytic/repositories/analytics_repository.py](file:///d:/CRM%20agent/demo_analytic/repositories/analytics_repository.py)
* [demo_analytic/schemas/__init__.py](file:///d:/CRM%20agent/demo_analytic/schemas/__init__.py)
* [demo_analytic/schemas/agent_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py)
* [demo_analytic/schemas/churn_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py)
* [demo_analytic/schemas/dashboard_snapshot.py](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py)
* [demo_analytic/schemas/intent_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py)
* [demo_analytic/schemas/knowledge_gap.py](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py)
* [demo_analytic/schemas/language_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py)
* [demo_analytic/schemas/roi_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py)
* [demo_analytic/schemas/satisfaction_metrics.py](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py)
* [demo_analytic/services/__init__.py](file:///d:/CRM%20agent/demo_analytic/services/__init__.py)
* [demo_analytic/services/churn_monitor_service.py](file:///d:/CRM%20agent/demo_analytic/services/churn_monitor_service.py)
* [demo_analytic/services/knowledge_gap_service.py](file:///d:/CRM%20agent/demo_analytic/services/knowledge_gap_service.py)
* [demo_analytic/tests/__init__.py](file:///d:/CRM%20agent/demo_analytic/tests/__init__.py)
* [demo_analytic/tests/test_agent_performance_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_agent_performance_service.py)
* [demo_analytic/tests/test_analytics_repository.py](file:///d:/CRM%20agent/demo_analytic/tests/test_analytics_repository.py)
* [demo_analytic/tests/test_churn_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_churn_analytics_service.py)
* [demo_analytic/tests/test_churn_monitor_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_churn_monitor_service.py)
* [demo_analytic/tests/test_dashboard_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_dashboard_service.py)
* [demo_analytic/tests/test_end_to_end_analytics_flow.py](file:///d:/CRM%20agent/demo_analytic/tests/test_end_to_end_analytics_flow.py)
* [demo_analytic/tests/test_intent_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_intent_analytics_service.py)
* [demo_analytic/tests/test_knowledge_gap_report_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_knowledge_gap_report_service.py)
* [demo_analytic/tests/test_knowledge_gap_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_knowledge_gap_service.py)
* [demo_analytic/tests/test_language_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_language_analytics_service.py)
* [demo_analytic/tests/test_roi_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_roi_analytics_service.py)
* [demo_analytic/tests/test_roi_report_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_roi_report_service.py)
* [demo_analytic/tests/test_satisfaction_analytics_service.py](file:///d:/CRM%20agent/demo_analytic/tests/test_satisfaction_analytics_service.py)
* [demo_analytic/.gitignore](file:///d:/CRM%20agent/demo_analytic/.gitignore)
* [demo_analytic/README.md](file:///d:/CRM%20agent/demo_analytic/README.md)
* [demo_analytic/__init__.py](file:///d:/CRM%20agent/demo_analytic/__init__.py)

### Main Components

#### Repositories
* [AnalyticsRepository](file:///d:/CRM%20agent/demo_analytic/repositories/analytics_repository.py#L9)

#### Services
* [AgentPerformanceAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/agent_performance_service.py#L9)
* [ChurnAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/churn_analytics_service.py#L8)
* [IntentAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/intent_analytics_service.py#L9)
* [LanguageAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/language_analytics_service.py#L9)
* [ROIAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/roi_analytics_service.py#L9)
* [SatisfactionAnalyticsService](file:///d:/CRM%20agent/demo_analytic/analytics/satisfaction_analytics_service.py#L9)
* [DashboardService](file:///d:/CRM%20agent/demo_analytic/dashboard/dashboard_service.py#L30)
* [ChurnMonitorService](file:///d:/CRM%20agent/demo_analytic/services/churn_monitor_service.py#L7)
* [KnowledgeGapService](file:///d:/CRM%20agent/demo_analytic/services/knowledge_gap_service.py#L7)
* [ExecutiveSummaryService](file:///d:/CRM%20agent/demo_analytic/reports/executive_summary_service.py#L7)
* [KnowledgeGapReportService](file:///d:/CRM%20agent/demo_analytic/reports/knowledge_gap_report_service.py#L5)
* [ROIReportService](file:///d:/CRM%20agent/demo_analytic/reports/roi_report_service.py#L6)

#### Schemas
* [AgentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/agent_metrics.py#L8)
* [ChurnMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L18)
* [DashboardSnapshot](file:///d:/CRM%20agent/demo_analytic/schemas/dashboard_snapshot.py#L16)
* [IntentMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L11)
* [KnowledgeGap](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L20)
* [LanguageMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L20)
* [ROIMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/roi_metrics.py#L8)
* [SatisfactionMetrics](file:///d:/CRM%20agent/demo_analytic/schemas/satisfaction_metrics.py#L7)
* [Settings](file:///d:/CRM%20agent/demo_analytic/config/settings.py#L4)

#### Enums (Literals)
* [ChurnRiskTier](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L7)
* [RiskDriverType](file:///d:/CRM%20agent/demo_analytic/schemas/churn_metrics.py#L9)
* [Layer1IntentType](file:///d:/CRM%20agent/demo_analytic/schemas/intent_metrics.py#L8)
* [GapSeverityTier](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L8)
* [GapActionType](file:///d:/CRM%20agent/demo_analytic/schemas/knowledge_gap.py#L11)
* [SupportedISOLanguages](file:///d:/CRM%20agent/demo_analytic/schemas/language_metrics.py#L8)

#### Utilities / Mappers
* [CustomerMapper](file:///d:/CRM%20agent/demo_analytic/integrations/customer_mapper.py#L5)
* [FeedbackMapper](file:///d:/CRM%20agent/demo_analytic/integrations/feedback_mapper.py#L5)
* [TranscriptMapper](file:///d:/CRM%20agent/demo_analytic/integrations/transcript_mapper.py#L6)
* [TranslationMapper](file:///d:/CRM%20agent/demo_analytic/integrations/translation_mapper.py#L6)
* [EmailDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/email_dispatcher.py#L12)
* [SlackDispatcher](file:///d:/CRM%20agent/demo_analytic/dispatchers/slack_dispatcher.py#L9)

#### View Managers
* [ViewManager](file:///d:/CRM%20agent/demo_analytic/materialized_views/view_manager.py#L16)

#### Graphs
None

### Input / Output

#### Input
* Database row lists queried from `ticket_transcripts`, `translation_records`, and `customers`.
* Parameter datetimes governing reporting ranges and preceding window baselines.
* Standard configuration variables validated through environment parameters.

#### Output
* Fully validated `DashboardSnapshot` JSON instances detailing compiled domain metrics.
* Formatted ROI, executive overview, and gap text reports.
* SMTP and Slack messages directed to webhook and SMTP address routes.
* Recreated Unique Indexes and concurrently refreshed SQL materialized views.

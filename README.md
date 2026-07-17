<div align="center">

# 🚀 Enterprise AI-Powered Multi-Agent Customer Support Platform

### Production-Ready Enterprise Customer Support Automation powered by LangGraph, FastAPI, Groq Llama 3.3, PostgreSQL and Intelligent Multi-Agent Orchestration

<p align="center">

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>

<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>

<img src="https://img.shields.io/badge/LangGraph-121212?style=for-the-badge"/>

<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=for-the-badge"/>

<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>

<img src="https://img.shields.io/badge/pgvector-336791?style=for-the-badge"/>

<img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>

<img src="https://img.shields.io/badge/HuggingFace-Spaces-FFD21E?style=for-the-badge"/>

<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>

</p>

---

### 🌐 Live Demo

**Frontend:** https://crm-agent-tau.vercel.app/

**Repository:** https://github.com/shiwan-mangate/Multi-AI-Agents-Customer-Support-Automation-System

---

*An enterprise-grade multilingual customer support platform that combines AI orchestration, specialized autonomous agents, human-in-the-loop governance, CRM intelligence, and proactive customer engagement into a single production-ready architecture.*

</div>

---

# 📖 Platform Overview

Modern customer support platforms must do more than simply answer user queries. Enterprise organizations require intelligent orchestration, multilingual communication, business-aware decision making, workflow governance, customer analytics, and proactive engagement—all while maintaining reliability, auditability, and scalability.

This project presents a **production-ready enterprise AI platform** that automates the complete customer support lifecycle using a layered multi-agent architecture.

Instead of relying on a single LLM to answer every request, the platform decomposes customer interactions into specialized workflows. Each incoming request is analyzed, enriched, prioritized, routed to a domain-specific AI agent, translated when necessary, persisted for auditability, and synchronized with CRM intelligence before finally delivering a personalized response to the customer.

Unlike conventional chatbot implementations, the platform introduces:

- Intelligent AI orchestration using LangGraph
- Specialized domain agents with isolated workflows
- Human-in-the-Loop (HITL) approval for sensitive operations
- Multilingual inbound and outbound translation
- Persistent workflow execution using PostgreSQL checkpointers
- CRM intelligence and customer lifecycle management
- Autonomous proactive customer engagement
- Analytics-driven business insights

The result is a scalable architecture capable of supporting enterprise-grade customer operations while maintaining transparency, modularity, and operational governance.

---

# ✨ Platform Highlights

| Capability | Description |
|------------|-------------|
| 🤖 Multi-Agent Architecture | Independent specialist AI agents for FAQ, Refund, Account Management, Escalation, CRM Intelligence, and Proactive Engagement |
| 🧠 LangGraph Orchestration | Durable stateful workflows with checkpointing and resumable execution |
| 🌍 Multilingual Support | Automatic language detection, translation, localization, and response generation |
| 🎯 Intelligent Routing | AI Supervisor and Triage Engine determine the optimal specialist for every customer request |
| 👨‍💼 Human-in-the-Loop | Manager approval workflows for high-risk or policy-sensitive operations |
| 📊 CRM Intelligence | Customer profiling, analytics, event processing, feedback management, and churn monitoring |
| 🚀 Proactive AI | Autonomous background agent that detects churn risk and customer inactivity every 60 seconds |
| 💾 Persistent Workflows | PostgreSQL-backed workflow persistence with resumable execution |
| 🔍 Enterprise Observability | Audit logging, workflow tracking, customer timelines, and translation analytics |
| 🐳 Production Deployment | Containerized using Docker and deployed on Hugging Face Spaces |

---

# ⚡ Key Features

## Enterprise AI Orchestration

- AI Supervisor for intent classification
- Confidence-based intelligent routing
- Business-aware triage engine
- Durable workflow execution
- Shared dependency injection architecture

---

## Specialized AI Agents

- 📚 FAQ Agent (Retrieval-Augmented Generation)
- 💰 Refund Agent
- 🔐 Account Management Agent
- 🚨 Escalation Agent
- 📈 CRM Intelligence Agent
- 🤖 Proactive Customer Engagement Agent

---

## Human Governance

- LangGraph Interrupt-based approval workflow
- Manager review queue
- Workflow persistence
- Resume from checkpoint
- Audit logging

---

## Translation Intelligence

- Automatic language detection
- Native language response generation
- Translation validation
- Translation memory cache
- Entity protection
- Multilingual customer conversations

---

## CRM Intelligence

- Customer profile management
- Customer timeline generation
- Interaction history
- Feedback processing
- Customer analytics
- Churn score updates
- Event-driven CRM synchronization

---

## Proactive Customer Success

- Automatic CRM scanning
- Customer inactivity detection
- Churn prediction
- Risk assessment
- Automated outreach
- Escalation handoff

---

## Analytics Platform

- Agent performance analytics
- Language analytics
- Customer satisfaction metrics
- Intent analytics
- Knowledge gap detection
- Churn monitoring
- Executive dashboard generation

---

# 🏗️ Enterprise System Architecture

<div align="center">

<img src="images/MAIN IMAGE OF SYSTEM.png" width="100%">

</div>

---

# 🔄 High-Level Request Flow

Every customer interaction passes through a layered enterprise workflow designed to maximize automation while maintaining business governance.

```
Customer
        │
        ▼
API Gateway (FastAPI)
        │
        ▼
Layer 0
Input Processing
        │
        ▼
Inbound Translation Pipeline
        │
        ▼
Layer 1
AI Supervisor
        │
        ▼
Layer 2
Intelligent Triage
        │
        ▼
Specialist Agent
        │
        ▼
Human Approval (If Required)
        │
        ▼
Outbound Translation
        │
        ├────────────► Customer
        │
        ▼
CRM Intelligence
```

Meanwhile, a completely independent background pipeline continuously monitors customer behavior.

```
CRM Intelligence
        │
        ▼
Customer Profiles
        │
        ▼
Signal Detection
        │
        ▼
Proactive Agent
        │
        ├────────► Customer Outreach
        │
        ▼
Escalation Agent
```

---

# 🧩 High-Level Architecture

The platform follows a layered enterprise architecture where every layer owns a single business responsibility.

### Layer 0 — Input Processing & Language Intelligence

Receives customer requests, normalizes incoming payloads, enriches customer context, detects the customer's language, performs translation when necessary, and generates a unified ticket contract for downstream AI workflows.

---

### Layer 1 — AI Supervisor

Acts as the platform's intelligent orchestrator by classifying customer intent, extracting entities, analyzing sentiment, estimating confidence, and selecting the optimal processing path.

---

### Layer 2 — Intelligent Triage

Enriches requests using customer history, order context, SLA policies, and business rules before dispatching tickets to the most appropriate specialist AI agent.

---

### Specialist Agent Layer

Each business capability is implemented as an independent LangGraph workflow:

- FAQ Agent
- Refund Agent
- Account Agent
- Escalation Agent

Each agent owns its own state machine, business logic, validation policies, repositories, and workflow execution.

---

### Human-in-the-Loop Workflow

Sensitive business operations automatically pause execution using LangGraph Interrupts, allowing human managers to approve, reject, or modify decisions before workflow execution resumes from the exact checkpoint.

---

### Layer 3 — Outbound Translation

Transforms specialist responses into the customer's preferred language while preserving entities, formatting, and contextual information before delivering the final response.

---

### CRM Intelligence Layer

Every completed interaction updates customer timelines, profiles, analytics, feedback, churn scores, and operational metrics to create a continuously evolving customer intelligence platform.

---

### Background Proactive Intelligence

Operating independently of the reactive request pipeline, the Proactive Agent continuously scans CRM signals, detects customer inactivity and churn risks, performs autonomous outreach, and escalates high-risk cases for human review when necessary.

---

# 🏛️ Layer 0 — Input Processing & Language Intelligence

<div align="center">

<img src="images/Inbound-pipeline.png" width="95%">

</div>

---

Layer 0 serves as the platform's intelligent entry point. Every customer request—regardless of channel or language—is standardized into a canonical ticket before entering the AI orchestration pipeline.

Rather than exposing downstream agents to inconsistent payloads, Layer 0 performs normalization, language understanding, customer enrichment, and translation to guarantee that every subsequent workflow receives a clean, validated contract.

### Responsibilities

- Request Validation
- Payload Normalization
- Customer Context Enrichment
- Language Detection
- Entity Protection
- Translation Pipeline
- Translation Validation
- Translation Cache
- Unified Ticket Generation

### Workflow

```
Incoming Request
        │
        ▼
Request Validation
        │
        ▼
Language Detection
        │
        ▼
Entity Protection
        │
        ▼
Translation Engine
        │
        ▼
Translation Validation
        │
        ▼
Translation Cache
        │
        ▼
English Canonical Message
        │
        ▼
Unified Ticket
```

### Highlights

- Automatic multilingual support
- Translation fallback strategy
- Translation memory cache
- Protected business entities
- Standardized ticket schema
- Zero downstream language dependency

---

# 🧠 Layer 1 — AI Supervisor Orchestrator

Layer 1 functions as the decision-making brain of the platform.

Instead of sending requests directly to business agents, every ticket first passes through the AI Supervisor, which determines customer intent, urgency, confidence, and routing strategy.

The supervisor ensures that each request reaches the correct business workflow with the highest possible confidence.

### Responsibilities

- Intent Classification
- Entity Extraction
- Sentiment Analysis
- Urgency Detection
- Confidence Scoring
- Intelligent Routing

### Workflow

```
Unified Ticket
        │
        ▼
Intent Classification
        │
        ▼
Entity Extraction
        │
        ▼
Sentiment Analysis
        │
        ▼
Urgency Detection
        │
        ▼
Confidence Scoring
        │
        ▼
Route to Triage Engine
```

### Highlights

- AI-based routing
- Confidence-aware decisions
- Business-aware orchestration
- Standardized routing contract
- Independent from business logic

---

# 🎯 Intelligent Triage Engine

<div align="center">

<img src="images/Triage-agent.png" width="95%">

</div>

---

The Triage Engine enriches every request with business intelligence before handing it to a specialist AI agent.

Instead of relying solely on the customer's latest message, the triage workflow retrieves customer history, previous tickets, SLA policies, and operational context to make informed routing decisions.

### Responsibilities

- Customer Profile Retrieval
- Order Context Retrieval
- Historical Interaction Analysis
- Business Scoring
- Priority Assignment
- SLA Assignment
- Escalation Policy Evaluation
- Specialist Dispatch

### Workflow

```
Customer Lookup
        │
        ▼
Order Lookup
        │
        ▼
History Analysis
        │
        ▼
Business Scoring
        │
        ▼
Priority Assignment
        │
        ▼
SLA Assignment
        │
        ▼
Escalation Check
        │
        ▼
Specialist Dispatch
```

### Output

The triage engine produces a fully enriched ticket containing:

- Customer Profile
- Order Information
- Business Context
- Priority
- SLA
- Escalation Flags
- Recommended Specialist

---

# 🤖 Specialist Agent Layer

Once the request has been enriched by the Triage Engine, it is dispatched to one of four specialized LangGraph workflows.

Unlike monolithic chatbot systems, each specialist owns an independent workflow, dedicated business rules, repositories, policies, and response generation strategy.

The specialist layer consists of:

- 📚 FAQ Agent
- 💰 Refund Agent
- 🔐 Account Agent
- 🚨 Escalation Agent

Each workflow is independently checkpointed using PostgreSQL-backed LangGraph persistence, enabling resumable execution and enterprise-grade reliability.

---

# 📚 FAQ Agent

<div align="center">

<img src="images/FAQ-agent.png" width="95%">

</div>

---

The FAQ Agent provides Retrieval-Augmented Generation (RAG) capabilities for knowledge-intensive customer queries.

Instead of generating responses directly, the workflow validates the request, retrieves relevant knowledge, reranks results, expands contextual information, verifies the generated answer, and only responds when confidence thresholds are satisfied.

### Responsibilities

- Contract Validation
- Query Understanding
- Ambiguity Detection
- Clarification Handling
- Retrieval Strategy Selection
- Vector Search
- Candidate Re-ranking
- Parent Context Expansion
- Answer Generation
- Answer Verification
- Confidence Gate
- Escalation Handoff

### Workflow

```
Validate Request
        │
        ▼
Understand Query
        │
        ▼
Ambiguity Check
        │
        ├────► Clarification
        │
        ▼
Knowledge Retrieval
        │
        ▼
Re-ranking
        │
        ▼
Context Expansion
        │
        ▼
LLM Answer Generation
        │
        ▼
Verification
        │
        ▼
Confidence Gate
      ┌──┴─────┐
      ▼        ▼
 Respond   Escalation
```

### Highlights

- Retrieval-Augmented Generation
- Vector Search using pgvector
- Parent-child context retrieval
- Confidence-aware routing
- Knowledge gap detection

---

# 💰 Refund Agent

<div align="center">

<img src="images/Refund-agent.png" width="95%">

</div>

---

The Refund Agent automates refund processing while enforcing business policies, preventing duplicate executions, and supporting human approval for sensitive refund requests.

### Responsibilities

- Duplicate Detection
- Order Validation
- Customer Validation
- Refund Policy Evaluation
- Human Approval
- Refund Execution
- Audit Logging

### Workflow

```
Idempotency Check
        │
        ▼
Order Lookup
        │
        ▼
Customer Validation
        │
        ▼
Policy Engine
      ┌──┴───────────┐
      ▼              ▼
Execute        Escalation
      │              │
      ▼              ▼
Human Review (if required)
        │
        ▼
Refund Execution
        │
        ▼
Audit Logging
```

### Highlights

- Policy-driven automation
- Duplicate protection
- Human approval workflow
- Transaction safety
- Complete audit trail

---

# 🔐 Account Agent

<div align="center">

<img src="images/account-agent.png" width="95%">

</div>

---

The Account Agent manages customer identity, account security, authentication workflows, billing operations, and account recovery.

The workflow emphasizes security by performing identity verification, abuse detection, risk analysis, and policy enforcement before executing any sensitive account operation.

### Responsibilities

- Issue Classification
- Identity Resolution
- Account Context Retrieval
- Abuse Detection
- Risk Assessment
- Verification Policy
- Idempotency Protection
- Password Reset
- Account Unlock
- Invoice Retrieval
- Billing History
- Security Escalation
- Audit Logging

### Workflow

```
Validate Request
        │
        ▼
Issue Classification
        │
        ▼
Identity Resolution
        │
        ▼
Account Context
        │
        ▼
Risk Assessment
        │
        ▼
Verification Policy
        │
        ▼
Execution Decision
      ┌────┼─────────────┐
      ▼    ▼             ▼
Reset Unlock Billing Security
      │    │             │
      └────┴─────────────┘
              │
              ▼
        Audit Logging
              │
              ▼
       Response Generation
```

### Highlights

- Identity verification
- Fraud prevention
- Risk-aware execution
- Security-first workflow
- Policy-based automation

---

# 🚨 Escalation Agent

<div align="center">

<img src="images/escalation-agent.png" width="95%">

</div>

---

The Escalation Agent manages high-risk customer interactions requiring business oversight or human approval.

Rather than immediately forwarding every complex case, the workflow performs trigger assessment, customer enrichment, risk scoring, intelligent routing, and automated holding responses before creating a structured case for human reviewers.

### Responsibilities

- Contract Validation
- Trigger Assessment
- Duplicate Case Detection
- Customer Context
- Conversation Context
- Risk Scoring
- Intelligent Routing
- Holding Response Generation
- Human Brief Generation
- Human Review
- Notification Dispatch
- Case Persistence
- Final Response Generation

### Workflow

```
Validate Request
        │
        ▼
Trigger Assessment
        │
        ▼
Duplicate Check
        │
        ▼
Customer Context
        │
        ▼
Conversation Context
        │
        ▼
Risk Scoring
        │
        ▼
Routing Decision
        │
        ▼
Holding Response
        │
        ▼
Manager Brief
        │
        ▼
Human Review
        │
        ▼
Notification Dispatch
        │
        ▼
Case Persistence
        │
        ▼
Final Response
```

### Highlights

- Human-in-the-Loop governance
- Durable workflow persistence
- Manager approval queue
- Risk-based routing
- Notification orchestration
- Enterprise auditability

# 🧩 CRM Intelligence Layer

The CRM Intelligence Layer acts as the operational memory of the entire platform.

Unlike the specialist agents, the CRM layer does **not** directly interact with customers. Instead, it continuously captures every completed interaction, maintains customer profiles, updates business analytics, computes churn indicators, and becomes the primary data source for long-term customer intelligence.

Every specialist agent publishes standardized events to the CRM, enabling downstream analytics and proactive engagement without coupling business workflows.

---

## Responsibilities

- Customer Timeline Management
- Customer Profile Management
- Interaction History
- Event Processing
- Customer Feedback Storage
- Churn Score Updates
- Customer Analytics
- Customer Health Tracking

---

## CRM Data Flow

```text
Completed Specialist Workflow
            │
            ▼
     Standardized CRM Event
            │
            ▼
     Customer Timeline Update
            │
            ▼
      Customer Profile Update
            │
            ▼
      Analytics Aggregation
            │
            ▼
     Churn Score Calculation
            │
            ▼
 CRM Intelligence Database
```

---

### Key Characteristics

- Event-driven architecture
- Canonical customer profile
- Unified customer timeline
- Analytics-ready data model
- Shared by all specialist agents
- Foundation for proactive intelligence

---

# 🚀 Proactive Intelligence Agent

<div align="center">

<img src="images/proactive-agent.png" width="95%">

</div>

---

Unlike traditional customer support systems that only react after customers create tickets, the Proactive Intelligence Agent continuously monitors CRM intelligence and initiates customer engagement before problems escalate.

Running independently in the background every **60 seconds**, it scans customer profiles, churn indicators, inactivity signals, and interaction history to identify customers requiring proactive attention.

Low-risk scenarios trigger automated outreach, while high-risk situations are seamlessly handed off to the Escalation Agent for human review.

---

## Responsibilities

- CRM Signal Detection
- Customer Context Retrieval
- Suppression Policy
- Signal Analysis
- Risk Scoring
- Outreach Decision
- Personalized Message Generation
- Escalation Handoff

---

## Workflow

```text
CRM Signal
      │
      ▼
Validate Signal
      │
      ▼
Customer Context
      │
      ▼
Suppression Gate
      │
      ▼
Signal Analysis
      │
      ▼
Risk Scoring
      │
      ▼
Outreach Decision
   ┌──────┴─────────┐
   ▼                ▼
Generate       Escalation
Message         Handoff
   │                │
   └──────┬─────────┘
          ▼
   Final Response
```

---

### Signal Sources

- High Churn Risk
- VIP Retention Risk
- Customer Inactivity
- Negative Interaction Trends
- CRM Analytics
- Business Rules

---

### Highlights

- Autonomous background execution
- Customer health monitoring
- Churn prevention
- Intelligent suppression policies
- Automated outreach
- Human escalation for critical cases

---

# 🌍 Layer 3 — Inbound Translation Pipeline

<div align="center">

<img src="images/Inbould-pipeline.png" width="95%">

</div>

---

The Inbound Translation Pipeline enables true multilingual customer support.

Instead of forcing downstream AI agents to understand multiple languages, every incoming customer message is automatically detected, protected, translated into English, validated, and standardized before entering the orchestration pipeline.

This creates a single canonical language for every AI workflow while preserving the customer's original message.

---

## Responsibilities

- Language Detection
- Entity Protection
- Translation
- Translation Validation
- Translation Cache
- English Canonical Message Generation
- Language Metadata Generation

---

## Workflow

```text
Customer Message
        │
        ▼
Language Detection
        │
        ▼
Protect Entities
        │
        ▼
Translation Engine
        │
        ▼
Translation Validation
        │
        ▼
Translation Cache
        │
        ▼
Restore Protected Data
        │
        ▼
Canonical English Message
```

---

### Highlights

- Automatic language detection
- Translation caching
- Translation fallback
- Entity preservation
- Canonical English processing
- Multilingual customer support

---

# 🌐 Layer 3 — Outbound Translation Pipeline

<div align="center">

<img src="images/outbound-pipeline.png" width="95%">

</div>

---

The Outbound Translation Pipeline converts English responses generated by specialist agents into the customer's preferred language before delivery.

Business identifiers, order numbers, customer names, and structured entities remain protected throughout translation, ensuring safe multilingual communication.

---

## Responsibilities

- Response Protection
- Translation
- Translation Validation
- Translation Cache
- Entity Restoration
- Native Language Response

---

## Workflow

```text
English Response
        │
        ▼
Protect Entities
        │
        ▼
Translation Engine
        │
        ▼
Translation Validation
        │
        ▼
Translation Cache
        │
        ▼
Restore Protected Data
        │
        ▼
Native Language Response
```

---

### Highlights

- Multilingual response generation
- Entity-safe translation
- Translation memory
- Automatic language personalization
- Customer-native communication

---

# 📊 Layer 4 — Analytics & Business Intelligence

<div align="center">

<img src="images/Analytics%20service.png" width="95%">

</div>

---

The Analytics Layer transforms operational customer support data into actionable business intelligence.

Rather than operating on raw database records, the analytics engine aggregates transcripts, customer interactions, language metrics, feedback, and churn indicators to generate executive dashboards and operational insights.

This layer powers customer success teams, business stakeholders, and proactive customer engagement strategies.

---

## Responsibilities

- Platform KPI Aggregation
- Agent Performance Analytics
- Intent Analytics
- Customer Satisfaction Analytics
- Language Analytics
- Churn Analytics
- Knowledge Gap Detection
- Executive Dashboard Generation

---

## Workflow

```text
CRM Database
      │
      ▼
Repository Layer
      │
      ▼
Data Mapping
      │
      ▼
Analytics Engines
      │
      ├── Agent Analytics
      ├── Intent Analytics
      ├── Satisfaction Analytics
      ├── Language Analytics
      ├── Churn Analytics
      └── Knowledge Gap Analysis
              │
              ▼
Dashboard Snapshot
              │
              ▼
Business Intelligence
```

---

## Analytics Modules

- Agent Performance Analytics
- Intent Distribution Analytics
- Customer Satisfaction Analytics
- Language Usage Analytics
- Churn Risk Analytics
- Knowledge Gap Detection
- Executive KPI Dashboard

---

### Dashboard Metrics

- Total Tickets
- Customer Growth
- Agent Performance
- Resolution Rate
- Customer Satisfaction
- Language Distribution
- Churn Risk
- High-Risk Customers
- Knowledge Gaps

---

### Highlights

- Executive business dashboards
- Real-time KPI aggregation
- Customer health monitoring
- Agent performance evaluation
- Predictive churn analysis
- Continuous knowledge improvement
- Business intelligence reporting

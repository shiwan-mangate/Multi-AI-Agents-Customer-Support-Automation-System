# Customer Stories (Schema-Compliant Master Matrix)

## Purpose

Defines the canonical business realities that drive:

* Database Seed Generation
* Integration Testing
* Agent Routing Validation
* CRM Profile Construction
* Churn Analytics
* Escalation Logic
* Translation Workflows
* End-to-End System Testing

All seed data must originate from one of these stories.

Every row inserted into the database must be traceable to a documented customer scenario.

---

# Story 1 — The Baseline (Happy Path)

## Test Coverage

* Triage Agent
* FAQ Agent
* Basic CRM Profiling

## Customer

Name: Rahul Sharma

Tier: premium

LTV: 1450.00

Language: en

## Commerce

Order #5050

Amount: 1450.00

Status: DELIVERED

Subscription:

* Premium Plan
* Active

## Security

* Failed Attempts: 0
* Account Locked: False

## Ticket History

### TKT-100

Message:

"Where can I find the user manual?"

Attributes:

* Intent: faq
* Sentiment: neutral
* Resolved: True

## Refund History

None

## Escalation History

None

## Expected Route

Layer 1 Triage
→ faq_agent
→ resolved

---

# Story 2 — Policy Edge Case (Refund + Idempotency)

## Test Coverage

* Refund Agent
* Policy Evaluation
* Idempotency Protection
* Analytics

## Customer

Name: Sarah Jenkins

Tier: standard

LTV: 250.00

Language: en

## Commerce

Order #6012

Amount: 125.00

Status: DELIVERED

Created: 45 days ago

Subscription:

* Standard Plan
* Active

## Security

* Failed Attempts: 0
* Account Locked: False

## Ticket History

### TKT-200

Intent: refund_request

Sentiment: frustrated

Resolved: False

## Refund History

Customer submitted three identical refund requests.

Expected Result:

* Duplicate suppression
* Human review required

## Escalation History

None

## Expected Route

Layer 1 Triage
→ refund_agent

---

# Story 3 — Enterprise Multilingual Meltdown

## Test Coverage

* Translation Node
* VIP Routing
* Escalation Agent

## Customer

Name: Mateo Rodriguez

Tier: enterprise

LTV: 5000.00

Language: es

## Commerce

Order #7777

Amount: 2000.00

Status: PROCESSING

Subscription:

* VIP Enterprise
* Active

## Ticket History

### TKT-300

Intent: angry_complex

Sentiment: angry

Resolved: False

## Escalation History

Trigger Category:

* churn

Trigger Reason:

* vip_at_risk

## Expected Route

Translation Node
→ Layer 1 Triage
→ escalation_agent

Expected Risk Level:

CRITICAL

Expected Side Effects:

* escalation_case created
* notification_outbox entry created

---

# Story 4 — Security Lockout

## Test Coverage

* Account Agent
* Security Audit Logging

## Customer

Name: Anya Petrova

Tier: standard

LTV: 45.00

Language: en

## Security

Failed Attempts: 5

Account Locked: True

Suspicious Flag: True

## Ticket History

### TKT-400

Intent: account_issue

Sentiment: frustrated

Resolved: False

## Expected Route

Layer 1 Triage
→ account_agent

Expected Outcome:

VerificationLevel = FAILED

Decision = security_escalation

Expected Side Effects:

* account_security_audit record

---

# Story 5 — Silent Attrition

## Test Coverage

* CRM Engine
* Churn Calculation
* Proactive Agent
* Analytics

## Customer

Name: David Kim

Tier: premium

LTV: 2100.00

Language: en

## Commerce

Orders:

* 801
* 802
* 803

All Delivered

Subscription:

* Premium Plan
* past_due

## Ticket History

TKT-500

* technical_bug
* neutral
* unresolved

TKT-501

* technical_bug
* frustrated
* unresolved

TKT-502

* account_issue
* angry
* unresolved

## Escalation History

Trigger Category:

* sla

Trigger Reason:

* sla_breach_imminent

## Expected Route

Proactive Agent

Expected Output:

HIGH_CHURN_RISK

Expected Side Effects:

* customer_support_profile updated
* churn_alert generated

---

# Story 6 — Repeat Offender

## Test Coverage

* Triage Pattern Recognition
* Account Agent

## Customer

Name: Liam O'Connor

Tier: standard

LTV: 0.00

Language: en

Subscription:

* Trial
* Active

## Ticket History

TKT-600

* account_issue
* neutral
* resolved

TKT-601

* account_issue
* frustrated
* resolved

TKT-602

* account_issue
* angry
* unresolved

## Escalation History

Trigger Category:

* repeat_issue

Trigger Reason:

* repeat_issue_detected

## Expected Route

Layer 1 Triage
→ account_agent

Expected Outcome:

duplicate_suppressed

or

macro_resolution

---

# Story 7 — Billing Anomaly

## Test Coverage

* Account Agent
* Billing Analysis

## Customer

Name: Marcus Johnson

Tier: premium

LTV: 800.00

Language: en

## Commerce

Order #900

Amount: 800.00

Status: DELIVERED

## Billing History

inv-998

Amount: 100

inv-999

Amount: 100

Duplicate Charge

## Ticket History

### TKT-700

Intent: account_issue

Sentiment: frustrated

Resolved: False

## Expected Route

Layer 1 Triage
→ account_agent

Expected Outcome:

clarification_required

---

# Story 8 — Lost In Translation

## Test Coverage

* Translation Failure Handling
* Escalation Fallback

## Customer

Name: Hans Müller

Tier: standard

LTV: 100.00

Language: de

## Commerce

Order #1050

Amount: 100.00

Status: DELIVERED

## Ticket History

### TKT-800

Intent: faq

Sentiment: neutral

Resolved: False

## Failure Injection

Simulated translator failure.

Expected Translation Result:

translation_success = False

## Expected Route

Translation Node
→ Escalation Agent

Trigger Reason:

operational_low_confidence

Expected Side Effects:

* translation_record created
* escalation_case created
* notification_outbox queued

---

# Canonical Rule

Every database seed, integration test, workflow simulation, and analytics validation must originate from one of these stories.

These stories are the authoritative source for:

* Seed Generation
* Agent Testing
* Evaluation Suites
* Analytics Validation
* CRM State Construction
* End-to-End Workflow Verification

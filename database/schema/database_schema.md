# Database Schema (Phase 1 Freeze)

## Purpose

This document is the authoritative source of truth for the Multi-Agent Customer Support System database.

All agents, repositories, services, workflows, analytics jobs, and seed scripts must conform to this schema.

Any schema modification requires:

* Database Migration
* Repository Update
* Seed Data Update
* Documentation Update
* Test Update

---

# Database Domains

## Customer Domain

### customers

Purpose:
Master customer record and root entity of the system.

Primary Key:

* customer_id

Owns:

* Customer identity
* Email
* Tier
* Lifetime value
* Customer metadata

Referenced By:

* auth_accounts
* subscriptions
* orders
* refund_workflows
* refund_audit
* idempotency_keys
* escalation_cases
* account_security_audit

---

### customer_support_profiles

Purpose:
Aggregated CRM intelligence profile.

Contains:

* Ticket statistics
* Escalation statistics
* Churn metrics
* Sentiment history
* Language preferences

Type:
Derived / Aggregate Table

Relationship Status:
Application-managed relationship (FK not verified)

Warning:
Must remain synchronized with ticket and escalation activity.

---

### auth_accounts

Purpose:
Authentication and account security state.

Verified FK:

* customer_id → customers.customer_id

Contains:

* Failed login attempts
* Account lock state
* Security metadata

---

# Subscription Domain

### subscriptions

Purpose:
Subscription lifecycle management.

Primary Key:

* subscription_id

Verified FK:

* customer_id → customers.customer_id

Children:

* billing_history

---

### billing_history

Purpose:
Subscription payment history.

Primary Key:

* billing_id

Verified FK:

* customer_id → customers.customer_id
* subscription_id → subscriptions.subscription_id

Contains:

* Invoice history
* Payment records
* Billing events

---

# Commerce Domain

### orders

Purpose:
Customer purchase history.

Primary Key:

* order_id

Verified FK:

* customer_id → customers.customer_id

Referenced By:

* refund_workflows
* refund_audit
* processed_refunds

---

# Ticketing Domain

### tickets

Purpose:
Core support ticket entity.

Primary Key:

* ticket_id

Contains:

* Customer issue
* Sentiment
* Priority
* Resolution state
* Routing metadata

Referenced By:

* escalations
* active_workflows
* account_security_audit

---

### escalations

Purpose:
Basic ticket escalation tracking.

Primary Key:

* escalation_id

Verified FK:

* ticket_id → tickets.ticket_id

Contains:

* Escalation reason
* Escalation target
* Escalation timestamps

---

### ticket_transcripts

Purpose:
Stores support conversations.

Relationship Status:
Application-managed relationship (FK not verified)

Contains:

* Customer messages
* Agent responses
* Conversation history

---

### translation_records

Purpose:
Translation Agent persistence.

Relationship Status:
Application-managed relationship (FK not verified)

Contains:

* Source language
* Target language
* Translation output

---

# Refund Domain

### refund_workflows

Purpose:
Refund Agent workflow state.

Primary Key:

* workflow_id

Verified FK:

* customer_id → customers.customer_id
* order_id → orders.order_id

Children:

* refund_audit
* processed_refunds

---

### refund_audit

Purpose:
Immutable refund decision ledger.

Verified FK:

* customer_id → customers.customer_id
* order_id → orders.order_id

Contains:

* Policy evaluations
* Approval decisions
* Rejection reasons

---

### processed_refunds

Purpose:
Refund execution ledger.

Verified FK:

* order_id → orders.order_id

Contains:

* Refund execution records
* Idempotent refund tracking

---

# Escalation Domain

### escalation_cases

Purpose:
Advanced escalation management workflow.

Primary Key:

* case_id

Verified FK:

* customer_id → customers.customer_id

Children:

* escalation_audit
* escalation_feedback
* notification_outbox

---

### escalation_audit

Purpose:
Escalation decision audit trail.

Verified FK:

* case_id → escalation_cases.case_id

---

### escalation_feedback

Purpose:
Post-escalation outcome evaluation.

Verified FK:

* case_id → escalation_cases.case_id

---

### notification_outbox

Purpose:
Notification delivery queue.

Verified FK:

* case_id → escalation_cases.case_id

---

# Security Domain

### account_security_audit

Purpose:
Tracks security-related customer activity.

Verified FK:

* customer_id → customers.customer_id
* ticket_id → tickets.ticket_id

Contains:

* Login incidents
* Lockout events
* Security reviews

---

# Workflow Domain

### active_workflows

Purpose:
Tracks active AI workflows.

Verified FK:

* ticket_id → tickets.ticket_id

Contains:

* Workflow state
* Current node
* Agent ownership

---

### idempotency_keys

Purpose:
Prevents duplicate workflow execution.

Verified FK:

* customer_id → customers.customer_id

---

# CRM & Event Infrastructure

### crm_events

Purpose:
CRM event stream.

Relationship Status:
Application-managed

---

### processed_events

Purpose:
Event processing ledger.

Relationship Status:
Application-managed

---

### proactive_events

Purpose:
Customer engagement triggers.

Relationship Status:
Application-managed

---

### proactive_outreach_registry

Purpose:
Tracks proactive customer outreach.

Relationship Status:
Application-managed

---

# Analytics Domain

### churn_alerts

Purpose:
Customer churn monitoring.

Contains:

* Churn score
* Risk level
* Alert history

Type:
Derived / Aggregate Table

Relationship Status:
Application-managed relationship (FK not verified)

---

### feedback_signals

Purpose:
Stores customer feedback indicators.

Contains:

* Sentiment signals
* Satisfaction metrics
* Behavioral indicators

Type:
Analytical Table

Relationship Status:
Application-managed relationship (FK not verified)

---

# Verified Foreign Key Dependency Graph

customers
├── auth_accounts
├── subscriptions
│   └── billing_history
├── orders
│   ├── refund_workflows
│   ├── refund_audit
│   └── processed_refunds
├── escalation_cases
│   ├── escalation_audit
│   ├── escalation_feedback
│   └── notification_outbox
├── idempotency_keys
└── account_security_audit

tickets
├── escalations
├── active_workflows
└── account_security_audit

---

# Seeding Order

1. customers
2. subscriptions
3. orders
4. tickets
5. escalation_cases
6. auth_accounts
7. billing_history
8. refund_workflows
9. refund_audit
10. processed_refunds
11. idempotency_keys
12. escalations
13. active_workflows
14. account_security_audit
15. escalation_audit
16. escalation_feedback
17. notification_outbox
18. customer_support_profiles
19. ticket_transcripts
20. translation_records
21. churn_alerts
22. feedback_signals
23. crm_events
24. processed_events
25. proactive_events
26. proactive_outreach_registry

---

# Schema Integrity Rules

## Rule 1

Customers must exist before any dependent records.

---

## Rule 2

Orders must exist before refund-related records.

---

## Rule 3

Tickets must exist before:

* escalations
* active_workflows
* account_security_audit

---

## Rule 4

Escalation cases must exist before:

* escalation_audit
* escalation_feedback
* notification_outbox

---

## Rule 5

Derived tables must remain synchronized:

* customer_support_profiles
* churn_alerts

---

## Rule 6

Seed data must originate from canonical customer stories.

Never create orphaned records.

Always create data through a valid business flow:

Customer → Order → Ticket → Workflow → Audit Trail

---

# Schema Freeze Policy

This schema is frozen for implementation.

Any future change requires:

1. Migration
2. Repository Update
3. Seed Update
4. Documentation Update
5. Test Update

No direct schema modifications are allowed without updating all dependent components.

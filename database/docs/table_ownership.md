# Table Ownership Matrix

## Purpose

This document defines the authoritative ownership of every business fact in the system.

A business fact must have exactly one owner.

Ownership determines:

* Where data originates
* Which repository may write it
* Which tables are derived
* How seed data must be generated
* How integrity is maintained across all agents

---

# Ownership Categories

## SOURCE_OF_TRUTH

The table is the authoritative owner of the data.

Data should never be duplicated elsewhere as the primary source.

---

## DERIVED_AGGREGATE

Data is calculated from source tables.

Never manually invent values.

Must be generated from authoritative records.

---

## EVENT_LOG

Immutable operational history.

Records what happened.

Does not own customer state.

---

## AUDIT_LOG

Immutable compliance and traceability records.

Records decisions and actions.

---

## INFRASTRUCTURE

Supports orchestration, delivery, workflows, and idempotency.

Does not own business facts.

---

# CUSTOMER DOMAIN

## customers

Category:
SOURCE_OF_TRUTH

Owns:

* customer_id
* name
* email
* account_tier
* total_spent
* created_at

Referenced By:

* customer_support_profiles
* auth_accounts
* subscriptions
* orders
* tickets
* churn_alerts
* feedback_signals
* ticket_transcripts
* translation_records

---

## auth_accounts

Category:
SOURCE_OF_TRUTH

Owns:

* auth_account_id
* customer_id
* login_provider
* account_locked
* failed_login_attempts
* two_factor_enabled
* suspicious_flag
* last_login_at
* last_password_reset_at
* created_at
* updated_at

Used By:

* Account Agent

---

# SUBSCRIPTION DOMAIN

## subscriptions

Category:
SOURCE_OF_TRUTH

Owns:

* subscription_id
* customer_id
* plan_name
* billing_cycle
* status
* auto_renew
* started_at
* renews_at
* cancelled_at
* created_at
* updated_at

Used By:

* Account Agent
* Churn Engine
* Proactive Agent

---

## billing_history

Category:
SOURCE_OF_TRUTH

Owns:

* billing_id
* customer_id
* subscription_id
* invoice_id
* charge_amount
* currency
* charge_type
* status
* created_at

Used By:

* Billing Agent
* Account Agent

---

# ORDER DOMAIN

## orders

Category:
SOURCE_OF_TRUTH

Owns:

* order_id
* customer_id
* order_amount
* order_status
* created_at

Used By:

* Refund Agent
* Escalation Agent
* CRM Analytics

---

# TICKET DOMAIN

## tickets

Category:
SOURCE_OF_TRUTH

Owns:

* ticket_id
* customer_id
* issue_type
* sentiment
* priority
* resolved
* ticket_ref
* created_at

Used By:

* Layer 0
* Layer 1
* Triage Agent
* Refund Agent
* Account Agent
* Escalation Agent
* CRM Agent
* Analytics Agent

Children:

* escalations
* escalation_cases
* ticket_transcripts
* translation_records

---

# ESCALATION DOMAIN

## escalations

Category:
SOURCE_OF_TRUTH

Owns:

* escalation_id
* ticket_id
* reason
* escalated_to
* created_at

Used By:

* Triage Agent
* Escalation Agent
* CRM

---

## escalation_cases

Category:
SOURCE_OF_TRUTH

Owns:

* case_id
* ticket_id
* customer_id
* source_agent
* trigger_category
* trigger_reasons
* risk_score
* risk_level
* assigned_team
* status
* holding_sent
* holding_message
* human_brief
* recommended_action
* sla_deadline
* duplicate_of_case_id
* resolved_at
* created_at
* updated_at

Used By:

* Escalation Agent

---

## escalation_audit

Category:
AUDIT_LOG

Owns:

* audit_id
* case_id
* ticket_id
* event_type
* payload
* operator_type
* created_at

Written By:

* Escalation Agent

---

# REFUND DOMAIN

## refund_workflows

Category:
SOURCE_OF_TRUTH

Owns:

* workflow_id
* customer_id
* order_id
* workflow_status
* policy_decision
* refund_amount
* created_at

Used By:

* Refund Agent

---

## refund_audit

Category:
AUDIT_LOG

Owns:

* audit records
* decision history
* policy evaluations

Written By:

* Refund Agent

---

## processed_refunds

Category:
INFRASTRUCTURE

Owns:

* idempotency state
* execution history

Used By:

* Refund Agent

---

# TRANSLATION DOMAIN

## translation_records

Category:
EVENT_LOG

Owns:

* translation_id
* ticket_id
* customer_id
* source_language
* target_language
* original_text
* translated_text
* translation_success
* created_at

Used By:

* Translation Agent

---

# TRANSCRIPT DOMAIN

## ticket_transcripts

Category:
EVENT_LOG

Owns:

* transcript_id
* ticket_id
* customer_id
* conversation history
* resolution summary
* metadata

Written By:

* CRM Agent

---

# CRM DOMAIN

## customer_support_profiles

Category:
DERIVED_AGGREGATE

Source Tables:

* customers
* tickets
* escalations
* feedback_signals
* subscriptions
* crm_events

Stores:

* total_tickets
* total_faq_tickets
* total_refund_tickets
* total_account_tickets
* total_escalations
* total_denials
* total_failures
* total_clarifications
* total_duplicate_suppressions
* negative_ticket_count
* repeat_negative_count
* repeat_escalation_count
* duplicate_request_count
* last_sentiment
* sentiment_history
* issue_frequency
* agent_interaction_frequency

AI-Owned Fields:

* churn_score
* churn_level
* churn_last_updated

Rule:

Never manually invent aggregate values.

They must be derived from events and operational records.

---

## feedback_signals

Category:
SOURCE_OF_TRUTH

Owns:

* feedback_id
* ticket_id
* customer_id
* source_agent
* feedback_type
* rating
* comment
* feedback_channel
* resolution_type
* status
* processed_for_churn
* created_at

Used By:

* CRM Agent
* Churn Engine
* Analytics Agent

---

## churn_alerts

Category:
SOURCE_OF_TRUTH

Owns:

* alert_id
* customer_id
* ticket_id
* alert_type
* severity
* score
* reason
* risk_reasons
* alert_status
* delivery_status
* created_at

Used By:

* Proactive Agent
* CRM Agent

---

# EVENT INFRASTRUCTURE

## crm_events

Category:
EVENT_LOG

Owns:

* event_id
* event_type
* source_agent
* schema_version
* payload
* status
* retry_count
* claimed_by
* claimed_at
* processed_at
* last_error

Written By:

* CRM Event Processor

---

## processed_events

Category:
INFRASTRUCTURE

Owns:

* event_id
* processed_at
* result_status

Purpose:

CRM idempotency protection.

---

## idempotency_keys

Category:
INFRASTRUCTURE

Owns:

* idempotency_key
* action_type
* customer_id
* status
* response_payload
* created_at

Used By:

* Account Agent
* Refund Agent

---

## notification_outbox

Category:
INFRASTRUCTURE

Owns:

* notification_id
* case_id
* channel
* recipient
* payload
* status
* retry_count
* last_error
* processed_at
* created_at

Used By:

* Escalation Agent
* Proactive Agent

---

## account_security_audit

Category:
AUDIT_LOG

Owns:

* audit_id
* ticket_id
* customer_id
* workflow_id
* correlation_id
* action_type
* verification_level
* risk_score
* decision
* provider_response
* operator_type
* created_at

Written By:

* Account Agent

---

# Master Integrity Rules

Rule 1

customers is the root entity.

Every customer-dependent record must reference a valid customer.

---

Rule 2

tickets own support history.

No other table may redefine:

* issue_type
* sentiment
* priority
* resolved

---

Rule 3

orders own purchase history.

Refund workflows must reference orders.

---

Rule 4

escalations and escalation_cases own escalation state.

Customer profiles must never be used as escalation truth.

---

Rule 5

customer_support_profiles is an aggregate projection.

Operational tables remain authoritative.

---

Rule 6

Audit tables are append-only.

Never update historical audit records.

---

Rule 7

Event tables are immutable.

Events represent facts that occurred.

---

Rule 8

Infrastructure tables never own business facts.

They only support execution and reliability.

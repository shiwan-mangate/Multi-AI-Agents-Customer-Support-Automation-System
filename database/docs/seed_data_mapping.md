Seed Data Mapping (Final Schema-Aligned)
Purpose: This document maps each customer story to the exact database records that must be inserted into seeded tables. It serves as the definitive bridge between customer_stories.md and the SQL seed files. Generated tables are intentionally excluded.

Seeded Tables (System Inputs)
customers

auth_accounts

subscriptions

billing_history

orders

tickets

feedback_signals

Story 1 — Rahul Sharma (Baseline)
customers

customer_id = 1

name = Rahul Sharma

email = rahul@example.com

account_tier = premium

total_spent = 1450.00

created_at = 2025-11-01T10:00:00Z

auth_accounts

auth_account_id = AUTH-1

customer_id = 1

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = true

suspicious_flag = false

created_at = 2025-11-01T10:00:00Z

updated_at = 2026-06-17T09:00:00Z

subscriptions

subscription_id = SUB-001

customer_id = 1

plan_name = Premium Plan

billing_cycle = monthly

status = active

auto_renew = true

started_at = 2025-11-01T10:00:00Z

renews_at = 2026-07-01T10:00:00Z

created_at = 2025-11-01T10:00:00Z

orders

order_id = 5050

customer_id = 1

order_amount = 1450.00

order_status = DELIVERED

created_at = 2026-06-01T10:00:00Z

tickets

ticket_id = TKT-100

customer_id = 1

issue_type = faq

sentiment = neutral

priority = low

resolved = true

ticket_ref = REF-100

created_at = 2026-06-18T10:00:00Z

Story 2 — Sarah Jenkins (Refund Edge Case)
customers

customer_id = 2

name = Sarah Jenkins

email = sarah@example.com

account_tier = standard

total_spent = 250.00

created_at = 2026-01-15T12:00:00Z

auth_accounts

auth_account_id = AUTH-2

customer_id = 2

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = false

suspicious_flag = false

created_at = 2026-01-15T12:00:00Z

subscriptions

subscription_id = SUB-002

customer_id = 2

plan_name = Standard Plan

billing_cycle = monthly

status = active

auto_renew = true

started_at = 2026-01-15T12:00:00Z

created_at = 2026-01-15T12:00:00Z

orders

order_id = 6012

customer_id = 2

order_amount = 125.00

order_status = DELIVERED

created_at = 2026-05-04T12:00:00Z (45 days ago)

tickets

ticket_id = TKT-200

customer_id = 2

issue_type = refund_request

sentiment = frustrated

priority = medium

resolved = false

ticket_ref = REF-200

created_at = 2026-06-18T11:00:00Z

Story 3 — Mateo Rodriguez (Enterprise Escalation)
customers

customer_id = 3

name = Mateo Rodriguez

email = mateo@example.com

account_tier = enterprise

total_spent = 5000.00

created_at = 2024-08-22T09:00:00Z

auth_accounts

auth_account_id = AUTH-3

customer_id = 3

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = true

suspicious_flag = false

created_at = 2024-08-22T09:00:00Z

subscriptions

subscription_id = SUB-003

customer_id = 3

plan_name = VIP Enterprise

billing_cycle = annual

status = active

auto_renew = true

started_at = 2024-08-22T09:00:00Z

created_at = 2024-08-22T09:00:00Z

orders

order_id = 7777

customer_id = 3

order_amount = 2000.00

order_status = PROCESSING

created_at = 2026-06-17T15:00:00Z

tickets

ticket_id = TKT-300

customer_id = 3

issue_type = angry_complex

sentiment = angry

priority = urgent

resolved = false

ticket_ref = REF-300

created_at = 2026-06-18T12:00:00Z

Story 4 — Anya Petrova (Security Lockout)
customers

customer_id = 4

name = Anya Petrova

email = anya@example.com

account_tier = standard

total_spent = 45.00

created_at = 2026-05-10T14:00:00Z

auth_accounts

auth_account_id = AUTH-4

customer_id = 4

login_provider = email

account_locked = true (Triggers Account Agent)

failed_login_attempts = 5

two_factor_enabled = false

suspicious_flag = true

created_at = 2026-05-10T14:00:00Z

updated_at = 2026-06-18T11:55:00Z

subscriptions

subscription_id = SUB-004

customer_id = 4

plan_name = Standard Plan

billing_cycle = monthly

status = active

auto_renew = true

started_at = 2026-05-10T14:00:00Z

created_at = 2026-05-10T14:00:00Z

orders

order_id = 1001

customer_id = 4

order_amount = 45.00

order_status = DELIVERED

created_at = 2026-05-11T10:00:00Z

tickets

ticket_id = TKT-400

customer_id = 4

issue_type = account_issue

sentiment = frustrated

priority = high

resolved = false

ticket_ref = REF-400

created_at = 2026-06-18T12:05:00Z

Story 5 — David Kim (High Churn Risk)
customers

customer_id = 5

name = David Kim

email = david@example.com

account_tier = premium

total_spent = 2100.00

created_at = 2025-02-14T08:00:00Z

auth_accounts

auth_account_id = AUTH-5

customer_id = 5

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = false

suspicious_flag = false

created_at = 2025-02-14T08:00:00Z

subscriptions

subscription_id = SUB-005

customer_id = 5

plan_name = Premium Plan

billing_cycle = monthly

status = past_due (Contributes to Churn Score)

auto_renew = true

started_at = 2025-02-14T08:00:00Z

created_at = 2025-02-14T08:00:00Z

**orders** 
*(Note: These represent chronological historical purchases across the customer lifecycle, demonstrating long-term loyalty prior to the June 2026 churn event.)*
*   order_id = 801 | customer_id = 5 | order_amount = 700.00 | order_status = DELIVERED | created_at = 2025-02-14T08:30:00Z (Initial purchase)
*   order_id = 802 | customer_id = 5 | order_amount = 700.00 | order_status = DELIVERED | created_at = 2025-08-10T10:15:00Z (Mid-year renewal/purchase)
*   order_id = 803 | customer_id = 5 | order_amount = 700.00 | order_status = DELIVERED | created_at = 2026-01-20T09:00:00Z (Recent purchase before churn risk)

tickets

ticket_id = TKT-500 | customer_id = 5 | issue_type = technical_bug | sentiment = neutral | priority = medium | resolved = false | ticket_ref = REF-500 | created_at = 2026-06-04T12:00:00Z

ticket_id = TKT-501 | customer_id = 5 | issue_type = technical_bug | sentiment = frustrated | priority = high | resolved = false | ticket_ref = REF-501 | created_at = 2026-06-11T12:00:00Z

ticket_id = TKT-502 | customer_id = 5 | issue_type = account_issue | sentiment = angry | priority = urgent | resolved = false | ticket_ref = REF-502 | created_at = 2026-06-18T12:00:00Z

feedback_signals (Required Schema Fields Added)

feedback_id = FB-501

ticket_id = TKT-501

customer_id = 5

source_agent = crm_agent

feedback_type = support_csat

rating = 1

comment = "Nobody is answering me"

feedback_channel = email

resolution_type = unresolved

status = pending

processed_for_churn = false

created_at = 2026-06-13T09:00:00Z

Story 6 — Liam O'Connor (Repeat Offender)
customers

customer_id = 6

name = Liam O'Connor

email = liam@example.com

account_tier = standard

total_spent = 0.00

created_at = 2026-05-20T10:00:00Z

auth_accounts

auth_account_id = AUTH-6

customer_id = 6

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = false

suspicious_flag = false

created_at = 2026-05-20T10:00:00Z

subscriptions

subscription_id = SUB-006

customer_id = 6

plan_name = Trial

billing_cycle = monthly

status = active

auto_renew = false

started_at = 2026-05-20T10:00:00Z

created_at = 2026-05-20T10:00:00Z

tickets

ticket_id = TKT-600 | customer_id = 6 | issue_type = account_issue | sentiment = neutral | priority = low | resolved = true | ticket_ref = REF-600 | created_at = 2026-06-04T10:00:00Z

ticket_id = TKT-601 | customer_id = 6 | issue_type = account_issue | sentiment = frustrated | priority = medium | resolved = true | ticket_ref = REF-601 | created_at = 2026-06-11T10:00:00Z

ticket_id = TKT-602 | customer_id = 6 | issue_type = account_issue | sentiment = angry | priority = high | resolved = false | ticket_ref = REF-602 | created_at = 2026-06-18T10:00:00Z

Story 7 — Marcus Johnson (Billing Anomaly)
customers

customer_id = 7

name = Marcus Johnson

email = marcus@example.com

account_tier = premium

total_spent = 800.00

created_at = 2025-12-01T08:00:00Z

auth_accounts

auth_account_id = AUTH-7

customer_id = 7

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = false

suspicious_flag = false

created_at = 2025-12-01T08:00:00Z

subscriptions

subscription_id = SUB-007

customer_id = 7

plan_name = Premium Plan

billing_cycle = monthly

status = active

auto_renew = true

started_at = 2025-12-01T08:00:00Z

created_at = 2025-12-01T08:00:00Z

billing_history (Corrected to Match Schema)

billing_id = BILL-101 | customer_id = 7 | subscription_id = SUB-007 | invoice_id = inv-998 | charge_amount = 100.00 | currency = USD | charge_type = subscription | status = paid | created_at = 2026-06-01T00:00:00Z

billing_id = BILL-102 | customer_id = 7 | subscription_id = SUB-007 | invoice_id = inv-999 | charge_amount = 100.00 | currency = USD | charge_type = subscription | status = paid | created_at = 2026-06-01T00:05:00Z (Duplicate Charge)

orders

order_id = 900

customer_id = 7

order_amount = 800.00

order_status = DELIVERED

created_at = 2026-05-01T00:00:00Z

tickets

ticket_id = TKT-700

customer_id = 7

issue_type = account_issue

sentiment = frustrated

priority = medium

resolved = false

ticket_ref = REF-700

created_at = 2026-06-18T09:00:00Z

Story 8 — Hans Müller (Translation Failure)
customers

customer_id = 8

name = Hans Müller

email = hans@example.com

account_tier = standard

total_spent = 100.00

created_at = 2026-06-05T14:00:00Z

auth_accounts

auth_account_id = AUTH-8

customer_id = 8

login_provider = email

account_locked = false

failed_login_attempts = 0

two_factor_enabled = false

suspicious_flag = false

created_at = 2026-06-05T14:00:00Z

subscriptions

subscription_id = SUB-008

customer_id = 8

plan_name = Standard Plan

billing_cycle = monthly

status = active

auto_renew = true

started_at = 2026-06-05T14:00:00Z

created_at = 2026-06-05T14:00:00Z

orders

order_id = 1050

customer_id = 8

order_amount = 100.00

order_status = DELIVERED

created_at = 2026-06-10T00:00:00Z

tickets

ticket_id = TKT-800

customer_id = 8

issue_type = faq

sentiment = neutral

priority = low

resolved = false

ticket_ref = REF-800

created_at = 2026-06-18T10:30:00Z
# Seed Validation

Validation Date:
2026-06-20

## Row Counts

customers: 8
auth_accounts: 8
subscriptions: 8
billing_history: 2
orders: 9
tickets: 12
feedback_signals: 1

## Foreign Key Validation

auth_accounts -> customers : PASS

subscriptions -> customers : PASS

orders -> customers : PASS

tickets -> customers : PASS

## Constraint Fixes Applied

auth_accounts.login_provider
email -> local

subscriptions.billing_cycle
annual -> yearly

billing_history.charge_type
subscription_renewal -> renewal

## Result

Seed dataset validated successfully.

Status: APPROVED
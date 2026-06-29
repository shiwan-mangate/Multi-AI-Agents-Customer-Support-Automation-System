-- ==========================================================
-- BILLING HISTORY
-- Source: customer_stories.md
-- ==========================================================

INSERT INTO billing_history (
    customer_id,
    subscription_id,
    invoice_id,
    charge_amount,
    currency,
    charge_type,
    status,
    created_at
)
VALUES

-- Story 7 : Marcus Johnson
(
    7,
    7,
    'INV-998',
    100.00,
    'USD',
    'renewal',
    'paid',
    '2026-06-01T00:00:00Z'
),

(
    7,
    7,
    'INV-999',
    100.00,
    'USD',
    'renewal',
    'paid',
    '2026-06-01T00:05:00Z'
);
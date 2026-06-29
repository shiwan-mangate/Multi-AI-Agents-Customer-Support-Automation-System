-- ==========================================================
-- SUBSCRIPTIONS
-- Source: customer_stories.md
-- ==========================================================

INSERT INTO subscriptions (
    subscription_id,
    customer_id,
    plan_name,
    billing_cycle,
    status,
    auto_renew,
    started_at,
    renews_at,
    cancelled_at,
    created_at,
    updated_at
)
VALUES

-- Story 1 : Rahul Sharma
(
    1,
    1,
    'Premium Plan',
    'monthly',
    'active',
    TRUE,
    '2025-11-01T10:00:00Z',
    '2026-07-01T10:00:00Z',
    NULL,
    '2025-11-01T10:00:00Z',
    '2026-06-18T10:00:00Z'
),

-- Story 2 : Sarah Jenkins
(
    2,
    2,
    'Standard Plan',
    'monthly',
    'active',
    TRUE,
    '2026-01-15T12:00:00Z',
    '2026-07-15T12:00:00Z',
    NULL,
    '2026-01-15T12:00:00Z',
    '2026-06-18T12:00:00Z'
),

-- Story 3 : Mateo Rodriguez
(
    3,
    3,
    'Enterprise Plan',
    'yearly',
    'active',
    TRUE,
    '2024-08-22T09:00:00Z',
    '2026-08-22T09:00:00Z',
    NULL,
    '2024-08-22T09:00:00Z',
    '2026-06-18T12:00:00Z'
),

-- Story 4 : Anya Petrova
(
    4,
    4,
    'Standard Plan',
    'monthly',
    'active',
    TRUE,
    '2026-05-10T14:00:00Z',
    '2026-07-10T14:00:00Z',
    NULL,
    '2026-05-10T14:00:00Z',
    '2026-06-18T12:05:00Z'
),

-- Story 5 : David Kim
(
    5,
    5,
    'Premium Plan',
    'monthly',
    'past_due',
    TRUE,
    '2025-02-14T08:00:00Z',
    '2026-06-14T08:00:00Z',
    NULL,
    '2025-02-14T08:00:00Z',
    '2026-06-18T12:00:00Z'
),

-- Story 6 : Liam O''Connor
(
    6,
    6,
    'Trial Plan',
    'monthly',
    'active',
    FALSE,
    '2026-05-20T10:00:00Z',
    '2026-06-20T10:00:00Z',
    NULL,
    '2026-05-20T10:00:00Z',
    '2026-06-18T10:00:00Z'
),

-- Story 7 : Marcus Johnson
(
    7,
    7,
    'Premium Plan',
    'monthly',
    'active',
    TRUE,
    '2025-12-01T08:00:00Z',
    '2026-07-01T08:00:00Z',
    NULL,
    '2025-12-01T08:00:00Z',
    '2026-06-18T09:00:00Z'
),

-- Story 8 : Hans Müller
(
    8,
    8,
    'Standard Plan',
    'monthly',
    'active',
    TRUE,
    '2026-06-05T14:00:00Z',
    '2026-07-05T14:00:00Z',
    NULL,
    '2026-06-05T14:00:00Z',
    '2026-06-18T10:30:00Z'
);
-- ==========================================================
-- AUTH ACCOUNTS
-- Source: customer_stories.md
-- ==========================================================

INSERT INTO auth_accounts (
    customer_id,
    login_provider,
    account_locked,
    failed_login_attempts,
    two_factor_enabled,
    suspicious_flag,
    last_login_at,
    last_password_reset_at,
    created_at,
    updated_at
)
VALUES

-- Story 1 : Rahul Sharma
(
    1,
    'local',
    FALSE,
    0,
    TRUE,  -- Corrected to TRUE based on finalized mapping
    FALSE,
    '2026-06-17T09:00:00Z',
    '2026-05-01T10:00:00Z',
    '2025-11-01T10:00:00Z',
    '2026-06-17T09:00:00Z'
),

-- Story 2 : Sarah Jenkins
(
    2,
    'local',
    FALSE,
    0,
    FALSE,
    FALSE,
    '2026-06-15T12:00:00Z',
    '2026-04-01T09:00:00Z',
    '2026-01-15T12:00:00Z',
    '2026-06-15T12:00:00Z'
),

-- Story 3 : Mateo Rodriguez
(
    3,
    'local',
    FALSE,
    0,
    TRUE,
    FALSE,
    '2026-06-18T08:00:00Z',
    '2026-05-01T08:00:00Z',
    '2024-08-22T09:00:00Z',
    '2026-06-18T08:00:00Z'
),

-- Story 4 : Anya Petrova
(
    4,
    'local',
    TRUE,
    5,
    FALSE,
    TRUE,
    '2026-06-10T14:00:00Z',
    '2026-03-01T09:00:00Z',
    '2026-05-10T14:00:00Z',
    '2026-06-18T12:05:00Z'
),

-- Story 5 : David Kim
(
    5,
    'local',
    FALSE,
    0,
    FALSE, -- Corrected to FALSE based on finalized mapping
    FALSE,
    '2026-06-12T11:00:00Z',
    '2026-04-15T10:00:00Z',
    '2025-02-14T08:00:00Z',
    '2026-06-12T11:00:00Z'
),

-- Story 6 : Liam O''Connor
(
    6,
    'local',
    FALSE,
    0,
    FALSE,
    FALSE,
    '2026-06-18T09:30:00Z',
    '2026-06-11T10:00:00Z',
    '2026-05-20T10:00:00Z',
    '2026-06-18T09:30:00Z'
),

-- Story 7 : Marcus Johnson
(
    7,
    'local',
    FALSE,
    0,
    FALSE, -- Corrected to FALSE based on finalized mapping
    FALSE,
    '2026-06-16T08:00:00Z',
    '2026-05-20T09:00:00Z',
    '2025-12-01T08:00:00Z',
    '2026-06-16T08:00:00Z'
),

-- Story 8 : Hans Müller
(
    8,
    'local',
    FALSE,
    0,
    FALSE,
    FALSE,
    '2026-06-18T10:00:00Z',
    '2026-06-10T09:00:00Z',
    '2026-06-05T14:00:00Z',
    '2026-06-18T10:00:00Z'
);
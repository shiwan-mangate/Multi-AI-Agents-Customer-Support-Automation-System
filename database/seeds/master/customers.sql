-- customers.sql

INSERT INTO customers (
    customer_id,
    name,
    email,
    account_tier,
    total_spent,
    created_at
)
VALUES

(
    1,
    'Rahul Sharma',
    'rahul@example.com',
    'premium',
    1450.00,
    '2025-11-01T10:00:00Z'
),

(
    2,
    'Sarah Jenkins',
    'sarah@example.com',
    'standard',
    250.00,
    '2026-01-15T12:00:00Z'
),

(
    3,
    'Mateo Rodriguez',
    'mateo@example.com',
    'enterprise',
    5000.00,
    '2024-08-22T09:00:00Z'
),

(
    4,
    'Anya Petrova',
    'anya@example.com',
    'standard',
    45.00,
    '2026-05-10T14:00:00Z'
),

(
    5,
    'David Kim',
    'david@example.com',
    'premium',
    2100.00,
    '2025-02-14T08:00:00Z'
),

(
    6,
    'Liam O''Connor',
    'liam@example.com',
    'standard',
    0.00,
    '2026-05-20T10:00:00Z'
),

(
    7,
    'Marcus Johnson',
    'marcus@example.com',
    'premium',
    800.00,
    '2025-12-01T08:00:00Z'
),

(
    8,
    'Hans Müller',
    'hans@example.com',
    'standard',
    100.00,
    '2026-06-05T14:00:00Z'
);
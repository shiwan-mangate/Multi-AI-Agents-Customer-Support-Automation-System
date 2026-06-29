-- ==========================================================
-- FEEDBACK SIGNALS
-- Source: customer_stories.md
-- ==========================================================

INSERT INTO feedback_signals (
    feedback_id,
    ticket_id,
    customer_id,
    source_agent,
    feedback_type,
    rating,
    comment,
    feedback_channel,
    resolution_type,
    status,
    processed_for_churn,
    created_at
)
VALUES

-- ==========================================================
-- Story 5 : David Kim
-- ==========================================================
(
    'FDBK-001',
    'TKT-501',
    5,
    'account_agent',
    'negative_feedback',
    1,
    'Nobody is answering me',
    'support_ticket',
    'unresolved',
    'open',
    FALSE,
    '2026-06-13T09:00:00Z'
);
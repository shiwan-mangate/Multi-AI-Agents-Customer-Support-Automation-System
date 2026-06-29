# layer_4_analytics/materialized_views/customer_health_view.py

"""
Materialized View Definition: mv_customer_health

Purpose:
Pre-computes a consolidated snapshot of customer health signals by joining 
the `customers` and `ticket_transcripts` tables. Offloads complex joins and 
aggregations from the API so the Python Analytics layer can instantly calculate 
churn risk without scanning millions of rows.
"""

VIEW_NAME = "mv_customer_health"

CREATE_VIEW_SQL = f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {VIEW_NAME} AS
SELECT 
    -- Primary Keys (Mapped directly from the 'customers' schema)
    c.customer_id,
    c.name AS customer_name,
    
    -- Account Context
    c.account_tier,
    c.total_spent,
    
    -- Derived Health Signals (Aggregated from 'ticket_transcripts')
    COUNT(t.ticket_id) AS total_tickets,
    
    -- Count any ticket that is not successfully resolved
    COALESCE(SUM(CASE WHEN t.status != 'resolved' THEN 1 ELSE 0 END), 0) AS unresolved_ticket_count,
    
    -- Tracking negative experiences based on the 'sentiment_end' categorical string
    COALESCE(SUM(CASE WHEN t.sentiment_end = 'negative' THEN 1 ELSE 0 END), 0) AS negative_experience_count,
    
    -- Time of the customer's most recent interaction
    MAX(t.created_at AT TIME ZONE 'UTC') AS last_activity_date,
    
    -- Snapshot Temporal Anchor
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' AS snapshot_generated_at
FROM 
    customers c
LEFT JOIN 
    ticket_transcripts t ON c.customer_id = t.customer_id
GROUP BY 
    c.customer_id,
    c.name,
    c.account_tier,
    c.total_spent;
"""


CREATE_INDEX_SQL = f"""
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_customer_health_id 
ON {VIEW_NAME} (customer_id);
"""

DROP_VIEW_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {VIEW_NAME} CASCADE;
"""

REFRESH_VIEW_SQL = f"""
REFRESH MATERIALIZED VIEW CONCURRENTLY {VIEW_NAME};
"""
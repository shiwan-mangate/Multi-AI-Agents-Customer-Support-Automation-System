# layer_4_analytics/materialized_views/intent_distribution_view.py

"""
Materialized View Definition: mv_intent_distribution

Purpose:
Pre-aggregates Layer 1 routing decisions (intents) by day. 
Acts as a Daily Fact Table to offload volume counting from Python memory 
to the PostgreSQL engine, explicitly enforcing UTC boundaries to align 
with Pydantic schema constraints.
"""

VIEW_NAME = "mv_intent_distribution"

CREATE_VIEW_SQL = f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {VIEW_NAME} AS
SELECT 
    -- Time Dimension (Explicit UTC Normalization of 'timestamp with time zone')
    DATE(created_at AT TIME ZONE 'UTC') AS report_date,
    
    -- Grouping Key (Layer 1 Bucket)
    intent,
    
    -- Volume Metric (Explicitly counting the business key from the schema)
    COUNT(ticket_id) AS ticket_count
FROM 
    ticket_transcripts
WHERE 
    intent IS NOT NULL  -- Exclude malformed or pre-routed tickets
GROUP BY 
    DATE(created_at AT TIME ZONE 'UTC'),
    intent;
"""

# Composite Unique Index allows us to use REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE_INDEX_SQL = f"""
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_intent_dist_date_intent 
ON {VIEW_NAME} (report_date, intent);
"""

DROP_VIEW_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {VIEW_NAME} CASCADE;
"""

REFRESH_VIEW_SQL = f"""
REFRESH MATERIALIZED VIEW CONCURRENTLY {VIEW_NAME};
"""
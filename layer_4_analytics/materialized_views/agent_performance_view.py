# layer_4_analytics/materialized_views/agent_performance_view.py

"""
Materialized View Definition: mv_agent_performance

Purpose:
Pre-aggregates raw transcript volume, resolution states, and processing times 
by day and by agent. Acts as a Daily Fact Table to allow sub-second dashboard 
filtering across any custom date range, explicitly enforcing UTC boundaries.
"""

VIEW_NAME = "mv_agent_performance"

CREATE_VIEW_SQL = f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {VIEW_NAME} AS
SELECT 
    -- Time Dimension (Explicit UTC Normalization)
    DATE(created_at AT TIME ZONE 'UTC') AS report_date,
    
    -- Grouping Key
    resolved_by AS agent_name,
    
    -- Volume Metrics
    COUNT(*) AS tickets_handled,
    
    -- State Aggregations
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) AS escalated_count,
    
    -- Performance Metrics (Explicitly ignore 0/negative/NULL times for pure analytics)
    AVG(
        CASE 
            WHEN time_to_resolution_ms > 0 THEN time_to_resolution_ms 
            ELSE NULL 
        END
    ) / 1000.0 AS avg_resolution_time_seconds
FROM 
    ticket_transcripts
WHERE 
    resolved_by IS NOT NULL  -- Exclude unassigned/pending tickets
GROUP BY 
    DATE(created_at AT TIME ZONE 'UTC'),
    resolved_by;
"""

# Composite Unique Index allows us to use REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE_INDEX_SQL = f"""
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_agent_performance_date_name 
ON {VIEW_NAME} (report_date, agent_name);
"""

DROP_VIEW_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {VIEW_NAME} CASCADE;
"""

REFRESH_VIEW_SQL = f"""
REFRESH MATERIALIZED VIEW CONCURRENTLY {VIEW_NAME};
"""
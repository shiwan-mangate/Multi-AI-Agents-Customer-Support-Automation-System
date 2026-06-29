# layer_4_analytics/materialized_views/roi_metrics_view.py

"""
Materialized View Definition: mv_roi_metrics

Purpose:
Pre-aggregates ticket resolution states by customer and by day. 
Accelerates the ROI calculation pipeline so the dashboard can render 
financial savings for specific tenants instantly. Strictly separates 
database counting from Python financial calculations.
"""

VIEW_NAME = "mv_roi_metrics"

CREATE_VIEW_SQL = f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {VIEW_NAME} AS
SELECT 
    -- Time Dimension (Explicit UTC Normalization of 'timestamp with time zone')
    DATE(t.created_at AT TIME ZONE 'UTC') AS report_date,
    
    -- Customer Grouping Keys
    t.customer_id,
    c.name AS customer_name,
    
    -- Resolution State Aggregations (Counting explicit strings from schema)
    SUM(CASE WHEN t.resolution_type = 'AUTO_RESOLVED' THEN 1 ELSE 0 END) AS auto_resolved_count,
    SUM(CASE WHEN t.resolution_type = 'ESCALATED' THEN 1 ELSE 0 END) AS escalated_count
    
FROM 
    ticket_transcripts t
LEFT JOIN 
    customers c ON t.customer_id = c.customer_id  -- Explicit schema match
WHERE 
    t.customer_id IS NOT NULL  
    AND t.resolution_type IS NOT NULL  -- Exclude pending/in-progress tickets
GROUP BY 
    DATE(t.created_at AT TIME ZONE 'UTC'),
    t.customer_id,
    c.name;
"""

# Composite Unique Index allows us to use REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE_INDEX_SQL = f"""
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_roi_metrics_date_cust 
ON {VIEW_NAME} (report_date, customer_id);
"""

DROP_VIEW_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {VIEW_NAME} CASCADE;
"""

REFRESH_VIEW_SQL = f"""
REFRESH MATERIALIZED VIEW CONCURRENTLY {VIEW_NAME};
"""
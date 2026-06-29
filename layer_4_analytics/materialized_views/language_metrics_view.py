# layer_4_analytics/materialized_views/language_metrics_view.py

"""
Materialized View Definition: mv_language_metrics

Purpose:
Pre-aggregates translation volumes and success rates by day and by language. 
Acts as a Daily Fact Table based on the `translation_records` table, offloading 
volume counting from Python memory to the PostgreSQL engine while explicitly 
enforcing UTC boundaries.
"""

VIEW_NAME = "mv_language_metrics"

CREATE_VIEW_SQL = f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {VIEW_NAME} AS
SELECT 
    -- Time Dimension (Explicit UTC Normalization of 'timestamp with time zone')
    DATE(created_at AT TIME ZONE 'UTC') AS report_date,
    
    -- Grouping Key (Mapped directly from your CSV schema)
    original_language AS language_code,
    
    -- Volume Metrics (Counting explicit primary key)
    COUNT(id) AS translation_count,
    
    -- Success Aggregations (Boolean check from translation_success column)
    SUM(CASE WHEN translation_success = TRUE THEN 1 ELSE 0 END) AS successful_translations
FROM 
    translation_records
WHERE 
    original_language IS NOT NULL -- Exclude malformed translation rows
GROUP BY 
    DATE(created_at AT TIME ZONE 'UTC'),
    original_language;
"""

# Composite Unique Index allows us to use REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE_INDEX_SQL = f"""
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_lang_metrics_date_lang 
ON {VIEW_NAME} (report_date, language_code);
"""

DROP_VIEW_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {VIEW_NAME} CASCADE;
"""

REFRESH_VIEW_SQL = f"""
REFRESH MATERIALIZED VIEW CONCURRENTLY {VIEW_NAME};
"""
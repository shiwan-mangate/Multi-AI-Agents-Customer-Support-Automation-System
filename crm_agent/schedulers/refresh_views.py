import argparse
import logging
import os
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("refresh_views")


MATERIALIZED_VIEWS = [
    "mv_agent_performance",
    "mv_intent_weekly",
    "mv_churn_distribution",
    "mv_refund_metrics",
    "mv_faq_metrics",
    "mv_language_metrics",
]

def main():
    """
    OLAP Maintenance Scheduler.
    Refreshes materialized views to keep dashboards up-to-date.
    """
    parser = argparse.ArgumentParser(description="Refresh CRM Materialized Views.")
    
   
    parser.add_argument(
        "--concurrent", 
        action="store_true", 
        help="Use CONCURRENTLY when refreshing materialized views."
    )
    args = parser.parse_args()

    logger.info("Initializing Materialized View Refresh Job...")


    db_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:pass@localhost:5432/crm_db"
    )
    
    try:
        engine = create_engine(
            db_url, 
            pool_pre_ping=True, 
            isolation_level="AUTOCOMMIT"
        )
    except Exception as e:
        logger.critical("Failed to connect to database: %s", str(e))
        sys.exit(1)


    start_time = time.time()
    success_count = 0

    concurrent_flag = "CONCURRENTLY " if args.concurrent else ""

    with engine.connect() as connection:
        for view_name in MATERIALIZED_VIEWS:
            
            # Strict authorization check (SQL Injection safeguard)
            if view_name not in MATERIALIZED_VIEWS:
                logger.critical("Security Exception: Unauthorized view name %s", view_name)
                raise ValueError(f"Unauthorized view name: {view_name}")

            logger.info("Refreshing view: %s...", view_name)
            
            sql = f"REFRESH MATERIALIZED VIEW {concurrent_flag}{view_name};"
            
            try:
                # Bypassing Repositories: Pure DBA execution
                connection.execute(text(sql))
                logger.info("✅ SUCCESS: %s", view_name)
                success_count += 1
                
            except SQLAlchemyError as e:
                logger.error("❌ FAILED to refresh %s: %s", view_name, str(e))


    duration = round(time.time() - start_time, 2)
    
    failed_count = len(MATERIALIZED_VIEWS) - success_count
    
    logger.info(
        "Refresh Job Complete. Successfully refreshed %d/%d views in %.2fs. Failed: %d",
        success_count,
        len(MATERIALIZED_VIEWS),
        duration,
        failed_count
    )
    
    if failed_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
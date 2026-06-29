# layer_4_analytics/materialized_views/view_manager.py

import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine


from layer_4_analytics.materialized_views import agent_performance_view
from layer_4_analytics.materialized_views import intent_distribution_view
from layer_4_analytics.materialized_views import customer_health_view
from layer_4_analytics.materialized_views import language_metrics_view
from layer_4_analytics.materialized_views import roi_metrics_view

logger = logging.getLogger(__name__)

class ViewManager:
    """
    Database Infrastructure Orchestrator for Layer 4 OLAP.
    Handles the lifecycle (Creation, Indexing, and Concurrent Refreshing) 
    of all PostgreSQL Materialized Views.
    """

    def __init__(self, engine: Engine):
        """
        Expects an active SQLAlchemy Engine injected at runtime.
        """
        self.engine = engine
        
       
        self.view_modules = [
            agent_performance_view,
            intent_distribution_view,
            customer_health_view,
            language_metrics_view,
            roi_metrics_view
        ]

    def initialize_all_views(self) -> None:
        """
        Bootstraps the database. Executes CREATE VIEW and CREATE UNIQUE INDEX.
        This is typically run during application startup or CI/CD deployment.
        """
        logger.info("Starting OLAP View Initialization...")
        
     
        with self.engine.begin() as conn:
            for module in self.view_modules:
                try:
                    logger.info(f"Creating view and index for: {module.VIEW_NAME}")
                    conn.execute(text(module.CREATE_VIEW_SQL))
                    conn.execute(text(module.CREATE_INDEX_SQL))
                except Exception as e:
                    logger.error(f"Failed to initialize {module.VIEW_NAME}. Error: {str(e)}")
                    raise e
                    
        logger.info("OLAP View Initialization Complete.")

    def refresh_all_views(self) -> None:
        """
        Updates the data inside the views. Designed to be called by a background 
        Cron job or Celery worker every 5-15 minutes.
        """
        logger.info("Starting Concurrent Refresh of OLAP Views...")

        
        with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            for module in self.view_modules:
                try:
                    logger.info(f"Refreshing {module.VIEW_NAME}...")
                    conn.execute(text(module.REFRESH_VIEW_SQL))
                except Exception:

                    logger.exception(f"Failed to refresh {module.VIEW_NAME}")
                    
        logger.info("OLAP View Refresh Complete.")

    def drop_all_views(self) -> None:
        """
        Teardown method. Useful for resetting test databases or forcing a hard 
        schema recreation during major upgrades.
        """
        logger.warning("Dropping all OLAP Materialized Views...")
        
        with self.engine.begin() as conn:
            for module in self.view_modules:
                conn.execute(text(module.DROP_VIEW_SQL))
                
        logger.info("All OLAP Views Dropped.")
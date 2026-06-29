import os
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Force logs to show up neatly
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

load_dotenv()
if "DB_PASS" not in os.environ:
    os.environ["DB_PASS"] = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""

# 1. Borrow the database connection from your existing platform
from platform_orchestration.dependency_container import DependencyContainer

# 2. Import Layer 4 Components using your EXACT existing folder structure
from layer_4_analytics.materialized_views.view_manager import ViewManager
from layer_4_analytics.repositories.analytics_repository import AnalyticsRepository
from layer_4_analytics.dashboard.dashboard_service import DashboardService 
from layer_4_analytics.reports.executive_summary_service import ExecutiveSummaryService

def run_nightly_analytics():
    print("\n🚀 INITIALIZING LAYER 4 ANALYTICS ENGINE...")

    # Step 1: Connect to the Enterprise Database
    container = DependencyContainer()
    db_session = container.db

    # Step 2: Initialize and Refresh Materialized Views (Crucial for OLAP!)
    print("🔄 Refreshing Materialized Views in PostgreSQL...")
    
    # 🟢 THE FIX: Extract the raw Engine from the Session for the ViewManager
    db_engine = db_session.get_bind()
    view_manager = ViewManager(db_engine)
    
    # ⚠️ IMPORTANT: Because this is your FIRST run, we MUST initialize the views so Postgres creates them.
    view_manager.initialize_all_views() 
    view_manager.refresh_all_views()

    # Step 3: Initialize Repositories and Services (Repository correctly takes the Session)
    analytics_repo = AnalyticsRepository(db_session)
    dashboard_service = DashboardService(analytics_repo)
    summary_service = ExecutiveSummaryService()

    # Step 4: Define the Time Window (Last 30 Days)
    now = datetime.now(timezone.utc)
    period_end = now
    period_start = now - timedelta(days=30)
    prev_period_start = period_start - timedelta(days=30)
    prev_period_end = period_start

    print(f"📊 Crunching Data: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")

    try:
        # Step 5: Generate the Master JSON Snapshot
        snapshot = dashboard_service.generate_dashboard_snapshot(
            period_start=period_start,
            period_end=period_end,
            previous_period_start=prev_period_start,
            previous_period_end=prev_period_end,
            target_customer_id=1,            # Required by your dashboard_service
            target_customer_name="Customer 1", 
            cost_per_ticket=4.0,   
            platform_cost=199.0    
        )
        
        print("✅ SNAPSHOT GENERATED! Compiling Executive Summary...\n")

        # Step 6: Generate a Human-Readable Report from the Snapshot
        executive_report = summary_service.generate_summary(snapshot)

        print("="*70)
        print("📈 LAYER 4 EXECUTIVE SUMMARY")
        print("="*70)
        print(executive_report)
        print("="*70)

    except Exception as e:
        print(f"\n❌ Analytics Engine Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_nightly_analytics()
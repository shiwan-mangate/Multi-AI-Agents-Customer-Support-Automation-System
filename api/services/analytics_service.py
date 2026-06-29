import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status

from layer_4_analytics.analytics.roi_analytics_service import ROIAnalyticsService
from layer_4_analytics.integrations.transcript_mapper import TranscriptMapper
from layer_4_analytics.schemas.roi_metrics import ROIMetrics

from platform_orchestration.dependency_container import DependencyContainer
from layer_4_analytics.dashboard.dashboard_service import DashboardService
from layer_4_analytics.reports.executive_summary_service import ExecutiveSummaryService

from api.config import api_settings
from api.schemas.analytics_responses import MasterDashboardResponse

logger = logging.getLogger("api_analytics_service")

class AnalyticsService:
    def __init__(self, container: DependencyContainer):
        self.container = container
       
        self.repository = self.container.layer4_analytics_repository
        
        self.dashboard_service = DashboardService(self.repository)
        self.summary_service = ExecutiveSummaryService()

    def get_master_dashboard(
    self,
    days: int = 30,
    request_id: str = "unknown"
    ) -> MasterDashboardResponse:
            logger.info(f"[{request_id}] Generating Master Dashboard Monolith for {days} days")
            try:
                now = datetime.now(timezone.utc)
                period_end = now
                period_start = now - timedelta(days=days)
                prev_period_start = period_start - timedelta(days=days)
                prev_period_end = period_start


                snapshot = self.dashboard_service.generate_dashboard_snapshot(
                        period_start=period_start,
                        period_end=period_end,
                        previous_period_start=prev_period_start,
                        previous_period_end=prev_period_end,
                    )

                report_text = self.summary_service.generate_summary(snapshot)

                return MasterDashboardResponse(
                    generated_at=now,
                    summary_report=report_text,
                    snapshot=snapshot
                )

            except Exception as e:
                logger.error(f"[{request_id}] Analytics Engine Failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate the master analytics dashboard."
                )
            
    def get_customer_roi(self,customer_id: int,days: int = 30,request_id: str = "unknown",) -> ROIMetrics:

        logger.info(
            f"[{request_id}] Generating ROI report for customer {customer_id}"
        )

        try:
            now = datetime.now(timezone.utc)

            period_end = now
            period_start = now - timedelta(days=days)

            raw_rows = self.repository.get_roi_data(
                period_start=period_start,
                period_end=period_end,
                customer_id=customer_id,
            )

            mapped_rows = TranscriptMapper.map_roi_rows(raw_rows)
            print("=" * 60)
            print("ROI DEBUG")
            print("Rows:", len(mapped_rows))

            for row in mapped_rows[:10]:
                print(row)

            print("=" * 60)
            customer_name = (
                mapped_rows[0]["customer_name"]
                if mapped_rows
                else f"Customer {customer_id}"
            )

            return ROIAnalyticsService.calculate_roi_metrics(
                customer_id=customer_id,
                customer_name=customer_name,
                mapped_rows=mapped_rows,
                period_start=period_start,
                period_end=period_end,
                estimated_cost_per_ticket=getattr(
                    api_settings,
                    "ANALYTICS_COST_PER_TICKET",
                    4.0,
                ),
                platform_cost=getattr(
                    api_settings,
                    "ANALYTICS_PLATFORM_COST",
                    199.0,
                ),
            )

        except Exception as e:
            logger.error(
                f"[{request_id}] ROI Engine Failed: {e}",
                exc_info=True,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate ROI report.",
            )
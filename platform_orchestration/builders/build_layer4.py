# platform_orchestration/builders/build_layer4.py

from layer_4_analytics.repositories.analytics_repository import AnalyticsRepository

from layer_4_analytics.analytics.agent_performance_service import AgentPerformanceAnalyticsService as AgentPerformanceService
from layer_4_analytics.analytics.intent_analytics_service import IntentAnalyticsService
from layer_4_analytics.analytics.satisfaction_analytics_service import SatisfactionAnalyticsService
from layer_4_analytics.analytics.roi_analytics_service import ROIAnalyticsService
from layer_4_analytics.analytics.language_analytics_service import LanguageAnalyticsService
from layer_4_analytics.analytics.churn_analytics_service import ChurnAnalyticsService
from layer_4_analytics.dashboard.dashboard_service import DashboardService
from layer_4_analytics.reports.roi_report_service import ROIReportService
from layer_4_analytics.reports.knowledge_gap_report_service import KnowledgeGapReportService
from layer_4_analytics.reports.executive_summary_service import ExecutiveSummaryService
from layer_4_analytics.services.churn_monitor_service import ChurnMonitorService
from layer_4_analytics.services.knowledge_gap_service import KnowledgeGapService

def build_layer4(container):
    # Repositories
    container.layer4_analytics_repository = AnalyticsRepository(container.db)

    # Core Analytics Services
    container.agent_performance_service = AgentPerformanceService()
    container.intent_analytics_service = IntentAnalyticsService()
    container.satisfaction_analytics_service = SatisfactionAnalyticsService()
    container.roi_analytics_service = ROIAnalyticsService()
    container.language_analytics_service = LanguageAnalyticsService()
    container.churn_analytics_service = ChurnAnalyticsService()

    # Business Intelligence Services
    container.knowledge_gap_service = KnowledgeGapService()
    container.churn_monitor_service = ChurnMonitorService()

    # Dashboard Layer
    container.dashboard_service = DashboardService(repository=container.layer4_analytics_repository)

    # Reporting Layer
    container.roi_report_service = ROIReportService()
    container.knowledge_gap_report_service = KnowledgeGapReportService()
    container.executive_summary_service = ExecutiveSummaryService()
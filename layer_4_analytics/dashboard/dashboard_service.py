# layer_4_analytics/services/dashboard_service.py

from datetime import datetime, timezone
from typing import Optional, Union


from layer_4_analytics.schemas.dashboard_snapshot import DashboardSnapshot


from layer_4_analytics.repositories.analytics_repository import AnalyticsRepository


from layer_4_analytics.integrations.transcript_mapper import TranscriptMapper
from layer_4_analytics.integrations.feedback_mapper import FeedbackMapper
from layer_4_analytics.integrations.translation_mapper import TranslationMapper
from layer_4_analytics.integrations.customer_mapper import CustomerMapper

from layer_4_analytics.analytics.agent_performance_service import AgentPerformanceAnalyticsService
from layer_4_analytics.analytics.intent_analytics_service import IntentAnalyticsService
from layer_4_analytics.analytics.satisfaction_analytics_service import SatisfactionAnalyticsService
from layer_4_analytics.analytics.language_analytics_service import LanguageAnalyticsService
from layer_4_analytics.analytics.churn_analytics_service import ChurnAnalyticsService


from layer_4_analytics.services.knowledge_gap_service import KnowledgeGapService
from layer_4_analytics.services.churn_monitor_service import ChurnMonitorService


class DashboardService:
    """
    The Master Orchestrator for Layer 4 Analytics.
    Coordinates database reads, mapping normalizations, and all KPI engine 
    calculations to assemble the final DashboardSnapshot contract.
    """

    def __init__(self, repository: AnalyticsRepository):
       
        self.repository = repository

    def generate_dashboard_snapshot(
    self,
    period_start: datetime,
    period_end: datetime,
    previous_period_start: datetime,
    previous_period_end: datetime,
) -> DashboardSnapshot:
        """
        Executes the full Layer 4 data pipeline and strictly validates 
        timeline alignment against the DashboardSnapshot schema.
        """

        raw_summary = self.repository.get_platform_summary(period_start, period_end)
        
        raw_agent = self.repository.get_agent_data(period_start, period_end)
        
        raw_intent_curr = self.repository.get_intent_data(period_start, period_end)
        raw_intent_prev = self.repository.get_intent_data(previous_period_start, previous_period_end)
        
        raw_feedback_curr = self.repository.get_feedback_data(period_start, period_end)
        raw_feedback_prev = self.repository.get_feedback_data(previous_period_start, previous_period_end)
        
        raw_lang_curr = self.repository.get_language_data(period_start, period_end)
        raw_lang_prev = self.repository.get_language_data(previous_period_start, previous_period_end)
        
        raw_churn = self.repository.get_all_customer_churn_data()


        mapped_agent = TranscriptMapper.map_agent_rows(raw_agent)
        
        mapped_intent_curr = TranscriptMapper.map_intent_rows(raw_intent_curr)
        
        mapped_intent_prev = TranscriptMapper.map_intent_rows(raw_intent_prev)
        
        mapped_feedback_curr = FeedbackMapper.map_feedback_rows(raw_feedback_curr)
        mapped_feedback_prev = FeedbackMapper.map_feedback_rows(raw_feedback_prev)
        
        mapped_lang_curr = TranslationMapper.map_translation_rows(raw_lang_curr)

        print("=" * 60)
        print("Mapped language sample:")
        for row in mapped_lang_curr[:5]:
            print(row)
        print("=" * 60)
        mapped_lang_prev = TranslationMapper.map_translation_rows(raw_lang_prev)
        
       
        mapped_churn = CustomerMapper.map_customer_rows(raw_churn)

       
        agent_metrics = AgentPerformanceAnalyticsService.calculate_agent_metrics(
            mapped_rows=mapped_agent,
            period_start=period_start,
            period_end=period_end,
            satisfaction_lookup={}  
        )

        intent_metrics = IntentAnalyticsService.calculate_intent_metrics(
            current_rows=mapped_intent_curr,
            previous_rows=mapped_intent_prev,
            period_start=period_start,
            period_end=period_end
        )

        satisfaction_metrics = SatisfactionAnalyticsService.calculate_satisfaction_metrics(
            current_rows=mapped_feedback_curr,
            previous_rows=mapped_feedback_prev,
            period_start=period_start,
            period_end=period_end
        )


        language_metrics = LanguageAnalyticsService.calculate_language_metrics(
            current_rows=mapped_lang_curr,
            previous_rows=mapped_lang_prev,
            period_start=period_start,
            period_end=period_end,
            satisfaction_lookup={}
        )

        all_churn_metrics = ChurnAnalyticsService.calculate_churn_metrics(mapped_churn)
        high_risk_customers = ChurnMonitorService.get_high_risk_customers(all_churn_metrics)

        knowledge_gaps = KnowledgeGapService.calculate_knowledge_gaps(mapped_feedback_curr)


        return DashboardSnapshot(
           
            snapshot_id=f"snap_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}",
            
           
            generated_at=datetime.now(timezone.utc),
            
           
            report_period_start=period_start,
            report_period_end=period_end,
            
          
            total_tickets=raw_summary.get("total_tickets", 0),
            total_customers=raw_summary.get("total_customers", 0),
            
            
            agent_metrics=agent_metrics,
            intent_metrics=intent_metrics,
            satisfaction_metrics=satisfaction_metrics,
            language_metrics=language_metrics,
            high_risk_customers=high_risk_customers,
            knowledge_gaps=knowledge_gaps
        )
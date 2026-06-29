# platform_orchestration/builders/build_layer3.py

from layer_3.repositories.translation_repository import TranslationRepository

from layer_3.service.translation_service import TranslationService
from layer_3.service.background_tasks import BackgroundTasksService
from layer_3.storage.bilingual_store_service import BilingualStoreService
from layer_3.storage.translation_persistence_service import TranslationPersistenceService
from layer_3.storage.translation_analytics_service import TranslationAnalyticsService
from layer_3.detection.detection_service import DetectionService
from layer_3.detection.language_detector import LanguageDetector
from layer_3.detection.context_signal_resolver import ContextSignalResolver
from layer_3.detection.script_detector import ScriptDetector
from layer_3.pipeline.inbound_translation_pipeline import InboundTranslationPipeline
from layer_3.pipeline.outbound_translation_pipeline import OutboundTranslationPipeline
from layer_3.translation.helsinki_translator import HelsinkiTranslator
from layer_3.tone.tone_adjustment_service import ToneAdjustmentService
from layer_3.analytics.language_dashboard_service import LanguageDashboardService
from layer_3.analytics.language_metrics_service import LanguageMetricsService
from layer_3.analytics.materialized_view_manager import MaterializedViewManager
# Note: Reusing the MessageGenerationService logic here, ensuring no variable conflict.
from layer_2_proactive_agent.services.message_generation_service import MessageGenerationService
from layer_3.integrations.pre_layer0_translation_adapter import Layer0TranslationAdapter
import os
from pathlib import Path
def build_layer3(container):
    BASE_DIR = Path(__file__).resolve().parents[2]
    absolute_model_path = BASE_DIR / "models" / "lid.176.ftz"
    # Repositories
    container.translation_repository = TranslationRepository(container.db)

    # Services
    container.bilingual_store_service = BilingualStoreService(repository=container.translation_repository)
    container.translation_analytics_service = TranslationAnalyticsService(repository=container.translation_repository)
    container.translation_persistence_service = TranslationPersistenceService(repository=container.translation_repository)
    container.translation_service = TranslationService(repository=container.translation_repository)
    
    container.background_tasks_service = BackgroundTasksService(
        store_service=container.bilingual_store_service, 
        persistence_service=container.translation_persistence_service
    )
    
    container.detection_service = DetectionService(fasttext_model_path=absolute_model_path)
    container.language_detector = LanguageDetector(fasttext_model_path=absolute_model_path)
    container.context_signal_resolver = ContextSignalResolver()
    container.script_detector = ScriptDetector()
    container.inbound_translation_pipeline = InboundTranslationPipeline()
    container.outbound_translation_pipeline = OutboundTranslationPipeline()
    container.helsinki_translator = HelsinkiTranslator()
    container.tone_adjustment_service = ToneAdjustmentService()
    
    container.language_metrics_service = LanguageMetricsService(analytics_service=container.translation_analytics_service)
    container.language_dashboard_service = LanguageDashboardService(metrics_service=container.language_metrics_service)
    
    # Namespaced to avoid colliding with proactive message generator
    container.layer3_message_generation_service = MessageGenerationService(llm=container.llm)
    container.layer0_translation_adapter = Layer0TranslationAdapter(translation_service=container.translation_service, translation_analytics=container.translation_analytics_service, crm_repository=container.triage_customer_repository)
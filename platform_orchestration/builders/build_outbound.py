import logging
from layer_3.integrations.specialist_response_adapter import SpecialistResponseAdapter
from layer_3.integrations.crm_translation_adapter import CRMTranslationAdapter
from platform_orchestration.outbound_response_pipeline import OutboundResponsePipeline

logger = logging.getLogger(__name__)

def build_outbound(container) -> None:
    """
    Wires the Outbound Translation and CRM dispatch pipeline into the DependencyContainer.
    Must be called AFTER build_layer3() so that translation services exist.
    """
    logger.info("Building Outbound Response Pipeline...")

    # 1. Initialize the pristine Layer 2 -> Layer 3 -> CRM adapters
    specialist_adapter = SpecialistResponseAdapter()
    crm_adapter = CRMTranslationAdapter()

    # 2. Extract Layer 3 services (already built by build_layer3)
    translation_service = getattr(container, "translation_service", None)
    analytics_service = getattr(container, "translation_analytics_service", None)
    translation_repo = getattr(container, "translation_repository", None)

    if not translation_service or not analytics_service:
        logger.warning("Layer 3 services missing in container. Ensure build_layer3 runs first.")

    # 3. Build the Outbound Orchestrator
    outbound_pipeline = OutboundResponsePipeline(
        specialist_adapter=specialist_adapter,
        crm_adapter=crm_adapter,
        translation_service=translation_service,
        analytics_service=analytics_service,
        translation_repo=translation_repo
    )

    # 4. Attach to the global container
    container.outbound_response_pipeline = outbound_pipeline
    
    logger.info("Outbound Response Pipeline successfully wired into container.")
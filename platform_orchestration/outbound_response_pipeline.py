import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OutboundResponsePipeline:
    """
    Orchestrates the flow from a Layer 2 Specialist Agent output to a native-language
    customer response, subsequently dispatching the interaction to the CRM Layer 4 
    via an asynchronous Event Queue.
    """

    def __init__(
        self,
        specialist_adapter: Any,
        crm_adapter: Any,
        translation_service: Any,
        analytics_service: Any,
        translation_repo: Any,
        crm_event_repo: Any = None # Added for decoupled async event queuing
    ):
        self.specialist_adapter = specialist_adapter
        self.crm_adapter = crm_adapter
        self.translation_service = translation_service
        self.analytics_service = analytics_service
        self.translation_repo = translation_repo
        self.crm_event_repo = crm_event_repo

    def process(self, specialist_result: Any, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Executes the outbound pipeline and returns the translated response payload.
        """
        if not specialist_result:
            return None

        try:
            logger.info("OutboundPipeline | Starting outbound process for Customer %s", customer_id)


            profile = self.analytics_service.get_customer_language_profile(customer_id) or {}
            target_language = profile.get("preferred_language", "en")

            # 2. Adapt Layer 2 Output -> TranslationRequest
            translation_request = self.specialist_adapter.adapt(
                output=specialist_result, 
                target_language=target_language
            )
            logger.warning(
        "ESCALATION ADAPTER OUTPUT = %s",
        translation_request.model_dump()
        if hasattr(translation_request, "model_dump")
        else translation_request
    )

            logger.warning(
            "OUTBOUND INPUT | type=%s | payload=%s",
            type(specialist_result).__name__,
            specialist_result
        )
            
            logger.warning(
            "TRANSLATION REQUEST = %s",
            translation_request
        )

            if not translation_request:
                logger.warning("OutboundPipeline | Specialist adapter returned no translation request.")
                return None

            logger.info(
                "OutboundPipeline | Translating %s response to %s for Ticket %s",
                translation_request.source_agent,
                target_language,
                translation_request.ticket_id
            )

            # 3. Execute Outbound Translation (Includes formatting, tone adjustment, caching)
            translation_result = self.translation_service.process_outbound_response(
                ticket_id=translation_request.ticket_id,
                english_response=translation_request.english_response,
                target_language=translation_request.target_language,
                source_agent=translation_request.source_agent
            )


            if self.translation_repo and self.crm_adapter:
                db_record = self.translation_repo.get_by_ticket_id(translation_request.ticket_id)
                if db_record:
                    crm_event = self.crm_adapter.from_translation_record(db_record)
                    if crm_event:
                        if self.crm_event_repo:
                            # Drop into the queue for the background worker (Safe, retriable)
                            self.crm_event_repo.create_event(crm_event)
                            logger.info("OutboundPipeline | CRM Event queued successfully for Ticket %s", translation_request.ticket_id)
                        else:
                            # Fallback if queue isn't wired yet
                            self.crm_adapter.dispatch_to_crm(crm_event)
                else:
                    logger.warning(
                        "OutboundPipeline | Could not find translation record for CRM dispatch: %s",
                        translation_request.ticket_id
                    )

            # 5. Return the final customer-facing payload
            return {
                "agent": translation_request.source_agent,
                "english_response": translation_request.english_response,
                "customer_response": translation_result.translated_text,
                "target_language": target_language
            }

        except Exception as e:
            logger.exception("OutboundPipeline | Critical failure in outbound processing: %s", str(e))
            return None
import logging
from typing import Any, Dict, Optional

# Layer 0 Contracts
from layer_0.model import UnifiedTicket

logger = logging.getLogger(__name__)

class Layer0TranslationAdapter:
    """
    Orchestrates the conversion boundary between Layer 0 UnifiedTicket structures,
    Layer 3 Translation Engines, and the exact dictionary contract ingested by Layer 1.
    """

    def __init__(
        self, 
        translation_service: Any, 
        translation_analytics: Optional[Any] = None,
        crm_repository: Optional[Any] = None
    ):
        self.translation_service = translation_service
        self.translation_analytics = translation_analytics
        self.crm_repository = crm_repository

    def _get_customer_id(self, ticket_customer_id: Any) -> Optional[int]:
        """
        Responsibility 1: Enforce int customer_id routing across the platform.
        Fails safely by returning None, preventing phantom user '0' queries.
        """
        try:
            return int(ticket_customer_id)
        except (ValueError, TypeError):
            logger.error(f"Layer0Adapter | Invalid customer_id '{ticket_customer_id}'. Cannot cast to int.")
            return None

    def _gather_customer_crm_data(self, customer_id: int) -> Dict[str, Any]:
        """
        Responsibility 3: Gathers customer master data needed for Layer 1.
        """

        fallback = {
            "tier": "standard",
            "lifetime_value": 0.0,
            "previous_tickets": 0,
            "email": "unknown@example.com"
        }

        if self.crm_repository:
            try:
                customer = self.crm_repository.get_customer_by_id(
                    customer_id
                )
                logger.warning(
            "CUSTOMER LOOKUP | customer_id=%s | total_spent=%s",
            customer_id,
            customer.get("total_spent") if customer else None,
        )

                if customer:
                    return {
                        "tier": customer.get(
                            "account_tier",
                            fallback["tier"]
                        ),

                        "lifetime_value": float(
                            customer.get(
                                "total_spent",
                                fallback["lifetime_value"]
                            ) or 0
                        ),

                        "previous_tickets": 0,

                        "email": customer.get(
                            "email",
                            fallback["email"]
                        )
                    }

            except Exception as e:
                logger.warning(
                    f"Layer0TranslationAdapter | Customer lookup failed "
                    f"for CustomerID={customer_id}. Error={e}"
                )

        return fallback

    def _gather_language_context(self, customer_id: int, ticket_lang: str) -> Dict[str, Any]:
        """
        Responsibility 4: Build accurate language context using our TranslationAnalyticsService.
        """
        default_locales = {
            "hi": "hi-IN", "en": "en-US", "fr": "fr-FR", 
            "es": "es-ES", "de": "de-DE", "ar": "ar-SA"
        }
        fallback_locale = default_locales.get(ticket_lang.lower(), f"{ticket_lang}-US")

        context = {
            "preferred_language": ticket_lang,
            "language_history": [ticket_lang],
            "browser_locale": fallback_locale
        }

        if self.translation_analytics:
            try:
                profile = self.translation_analytics.get_customer_language_profile(customer_id)
                if profile and isinstance(profile, dict):
                    context["preferred_language"] = profile.get("preferred_language", ticket_lang)
                    context["language_history"] = profile.get("language_history", [ticket_lang])
            except Exception as e:
                logger.warning(f"Layer0TranslationAdapter | Analytics lookup failed for CustomerID={customer_id}. Error={e}")

        return context

    def to_supervisor_payload(self, ticket: UnifiedTicket) -> Optional[Dict[str, Any]]:
        """
        Responsibility 5 & 6: Processes inbound strings via TranslationService and maps
        the complete state context into the structural payload expected by Layer 1.
        """
        if not ticket or not ticket.message_text or not ticket.ticket_id:
            logger.error("Layer0TranslationAdapter | Invalid UnifiedTicket: missing ticket, message, or ticket_id.")
            return None

        safe_customer_id = self._get_customer_id(ticket.customer_id)
        if safe_customer_id is None:
            return None  

        crm_data = self._gather_customer_crm_data(safe_customer_id)
        layer3_context = self._gather_language_context(safe_customer_id, ticket.language)

        try:
            inbound_response = self.translation_service.process_inbound_message(
                ticket_id=ticket.ticket_id,
                customer_id=safe_customer_id,
                message=ticket.message_text,
                customer_context=layer3_context
            )

            if not inbound_response or not inbound_response.bilingual_message:
                logger.error(f"Layer0TranslationAdapter | Inbound processing failed for TicketID={ticket.ticket_id}")
                return None

            bilingual_msg = inbound_response.bilingual_message
            detected_lang = bilingual_msg.language_context.detected_language if bilingual_msg.language_context else ticket.language

            payload =  {
                "ticket_id": ticket.ticket_id,
                "customer": {
                    "customer_id": safe_customer_id,
                    "name": ticket.customer_name,
                    "email": crm_data["email"], 
                    "tier": crm_data["tier"],
                    "lifetime_value": crm_data["lifetime_value"],
                    "previous_tickets": crm_data["previous_tickets"]
                },
                "conversation_history": getattr(ticket,"conversation_history",[]),
                "message": {
                    "original": ticket.message_text,
                    "normalized": bilingual_msg.english_text,
                    "language": detected_lang
                },
                "metadata": {
                    "channel": ticket.channel,  
                    "timestamp": ticket.timestamp,
                    "priority": ticket.priority or "low"
                },
                "status": "normalized"
            }
            logger.warning(
            "SUPERVISOR PAYLOAD CUSTOMER = %s",
            payload["customer"]
        )
            return payload

        except Exception as e:
            logger.critical(f"Layer0TranslationAdapter | Execution boundary crashed for TicketID={ticket.ticket_id}. Error={e}")
            return None
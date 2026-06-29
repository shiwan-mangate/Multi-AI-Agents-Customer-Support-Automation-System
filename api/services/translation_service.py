import logging
from fastapi import HTTPException, status
from platform_orchestration.dependency_container import DependencyContainer

# Import your existing Layer 3 components
from layer_3.analytics.language_dashboard_service import LanguageDashboardService
from layer_3.service.translation_service import TranslationService as CoreTranslationService

from api.schemas.translation_requests import LiveTranslationRequest
from api.schemas.translation_responses import (
    CustomerTranslationHistoryResponse,
    TranslationRecordItem,
    LiveTranslationResponse,
    OperationsDashboardResponse
)

logger = logging.getLogger("api_translation_service")

class TranslationApiService:
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.repo = self.container.translation_repository
        
        self.dashboard_service: LanguageDashboardService = self.container.language_dashboard_service
        self.core_translation: CoreTranslationService = self.container.translation_service

    def get_operations_dashboard(self, limit: int = 100, request_id: str = "unknown") -> OperationsDashboardResponse:
        logger.info(f"[{request_id}] Fetching Translation Operations Dashboard")
        try:
            dashboard_data = self.dashboard_service.get_operations_dashboard(failure_limit=limit)
            return OperationsDashboardResponse(**dashboard_data)
        except Exception as e:
            logger.error(f"[{request_id}] Failed to load operations dashboard: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error generating translation dashboard.")

    def get_ticket_translation(self, ticket_id: str, request_id: str = "unknown") -> TranslationRecordItem:
        logger.info(f"[{request_id}] Fetching translation record for Ticket {ticket_id}")
        try:
            record = self.repo.get_by_ticket_id(ticket_id)
            if not record:
                raise HTTPException(status_code=404, detail=f"No translation record found for ticket {ticket_id}")
                
            return TranslationRecordItem(
                ticket_id=record.ticket_id,
                customer_id=record.customer_id,
                original_language=record.original_language,
                translation_success=record.translation_success,
                original_text=record.original_text,
                english_text=record.english_text,
                response_english=record.response_english,
                response_translated=record.response_translated,
                response_language=record.response_language,
                created_at=record.created_at
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch ticket translation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error retrieving translation record.")

    def get_customer_history(
        self, 
        customer_id: int, 
        limit: int = 100, 
        request_id: str = "unknown"
    ) -> CustomerTranslationHistoryResponse:
        
        logger.info(f"[{request_id}] Fetching translation history for Customer {customer_id} (limit: {limit})")
        try:
            records = self.repo.get_customer_history(customer_id)
            items = [
                TranslationRecordItem(
                    ticket_id=r.ticket_id,
                    customer_id=r.customer_id,
                    original_language=r.original_language,
                    translation_success=r.translation_success,
                    original_text=r.original_text,
                    english_text=r.english_text,
                    response_english=r.response_english,
                    response_translated=r.response_translated,
                    response_language=r.response_language,
                    created_at=r.created_at
                ) for r in records
            ][:limit] # 🟢 THE FIX: Safely slice the list to enforce the limit
            
            return CustomerTranslationHistoryResponse(
                customer_id=customer_id,
                total_records=len(items),
                history=items
            )
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch customer translations: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error retrieving translation history.")

    def live_translate(
        self, 
        ticket_id: str, 
        request: LiveTranslationRequest, 
        request_id: str = "unknown"
    ) -> LiveTranslationResponse:
        """Manually invokes Layer 3 outbound translation."""
        logger.info(f"[{request_id}] Executing live translation for Ticket {ticket_id}")
        try:
            result = self.core_translation.process_outbound_response(
                ticket_id=ticket_id,
                english_response=request.english_text,
                target_language=request.target_language,
                source_agent=request.source_agent
            )
            
            if not result.translation_success:
                raise HTTPException(status_code=502, detail="Upstream translation model failed to generate response.")

            return LiveTranslationResponse(
                ticket_id=ticket_id,
                target_language=request.target_language,
                translation_success=result.translation_success,
                translated_text=result.translated_text,
                provider_used=result.provider_used
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{request_id}] Live translation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error executing translation.")
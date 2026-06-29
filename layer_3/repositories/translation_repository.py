import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from layer_3.database.models.translation_record_model import TranslationRecordModel
from layer_3.schemas.translation_record import TranslationRecord  

logger = logging.getLogger(__name__)

class TranslationRepository:
    """
    Data Access Object (DAO) for Layer 3 Translation.
    Handles all persistence, retrieval, and analytical queries for translation history.
    Contains NO business, translation, or language detection logic.
    """

    def __init__(self, db: Session):
   
        self.db = db

    def create_record(self, record: TranslationRecord) -> TranslationRecordModel:
        """
        Stores the inbound translation immediately after a customer message is processed.
        Takes a Pydantic domain model to enforce strict architectural contracts.
        """
        try:
         
            record_data = record.model_dump()
            db_record = TranslationRecordModel(**record_data)
            
            self.db.add(db_record)
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
                
            self.db.refresh(db_record)
            
            logger.info(f"TranslationRecord created | Ticket={db_record.ticket_id}")
            return db_record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create TranslationRecord: {e}", exc_info=True)
            raise

    def get_by_ticket_id(self, ticket_id: str) -> Optional[TranslationRecordModel]:
        """
        Retrieves the exact translation record for a specific CRM ticket.
        """
        return self.db.query(TranslationRecordModel).filter(
            TranslationRecordModel.ticket_id == ticket_id
        ).first()

    def update_outbound_translation(
        self, 
        ticket_id: str, 
        response_english: str, 
        response_translated: str, 
        response_language: str
    ) -> bool:
        """
        Updates an existing inbound record with the asynchronous agent response.
        This completes the bidirectional audit trail.
        """
        record = self.get_by_ticket_id(ticket_id)
        
        if not record:
            logger.warning(f"Cannot update outbound translation. Record not found | Ticket={ticket_id}")
            return False

        try:
            record.response_english = response_english
            record.response_translated = response_translated
            record.response_language = response_language
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
                
            logger.info(f"Outbound translation updated | Ticket={ticket_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update outbound translation | Ticket={ticket_id} | Error: {e}", exc_info=True)
            return False

    def update_translation_failure(self, ticket_id: str) -> bool:
        """
        Marks a translation record as failed (e.g., if the Translator crashes 
        or the TranslationValidator catches an LLM hallucination).
        """
        record = self.get_by_ticket_id(ticket_id)
        
        if not record:
            logger.warning(f"Cannot update failure status. Record not found | Ticket={ticket_id}")
            return False

        try:
            record.translation_success = False
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
                
            logger.info(f"Translation marked as failed | Ticket={ticket_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update failure status | Ticket={ticket_id} | Error: {e}", exc_info=True)
            return False

    def translation_exists(self, ticket_id: str) -> bool:
        """
        Idempotency check. Prevents duplicate translations of the same customer message.
        """
        result = self.db.query(TranslationRecordModel.id).filter(
            TranslationRecordModel.ticket_id == ticket_id
        ).first()
        return result is not None

    # -------------------------------------------------------------------------

    def get_customer_history(self, customer_id: int) -> List[TranslationRecordModel]:
        """
        Retrieves the full translation history for a customer.
        """
        return self.db.query(TranslationRecordModel).filter(
            TranslationRecordModel.customer_id == customer_id
        ).order_by(TranslationRecordModel.created_at.desc()).all()

    def get_by_customer_and_language(self, customer_id: int, language: str) -> List[TranslationRecordModel]:
        """
        Retrieves customer history specific to a requested language.
        """
        return self.db.query(TranslationRecordModel).filter(
            TranslationRecordModel.customer_id == customer_id,
            TranslationRecordModel.original_language == language
        ).order_by(TranslationRecordModel.created_at.desc()).all()

    def get_failed_translations(self, limit: int = 100) -> List[TranslationRecordModel]:
        """
        Operational monitoring. Fetches recent failed translations for debugging.
        Utilizes SQLAlchemy .is_(False) for maximum dialect compatibility.
        """
        return self.db.query(TranslationRecordModel).filter(
            TranslationRecordModel.translation_success.is_(False)
        ).order_by(TranslationRecordModel.created_at.desc()).limit(limit).all()

    def get_recent_language_usage(self, days: int = 30) -> Dict[str, int]:
        """
        Aggregates inbound language volume over a specific time period.
        """
        threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        results = self.db.query(
            TranslationRecordModel.original_language, 
            func.count(TranslationRecordModel.id)
        ).filter(
            TranslationRecordModel.created_at >= threshold_date
        ).group_by(
            TranslationRecordModel.original_language
        ).all()

        return {lang: count for lang, count in results}

    def get_translation_metrics(self) -> Dict[str, int]:
        """
        High-level aggregation for operational dashboards.
        """
        total = self.db.query(func.count(TranslationRecordModel.id)).scalar() or 0
        success = self.db.query(func.count(TranslationRecordModel.id)).filter(
            TranslationRecordModel.translation_success.is_(True)
        ).scalar() or 0
        
        return {
            "total": total,
            "success": success,
            "failed": total - success
        }
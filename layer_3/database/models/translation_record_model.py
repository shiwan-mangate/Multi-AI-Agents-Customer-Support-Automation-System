from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

# Centralized Base imported from the platform's core session configuration
from crm_agent.db.base import Base

class TranslationRecordModel(Base):
    """
    Persistence model for all inbound and outbound translations.
    Acts as the audit trail for the Layer 3 Translation subsystem.
    """
    __tablename__ = "translation_records"

  
    id = Column(Integer, primary_key=True, autoincrement=True)


    ticket_id = Column(String(100), index=True, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)

  
    original_text = Column(Text, nullable=False)
    original_language = Column(String(10), index=True, nullable=False)
    english_text = Column(Text, nullable=False)


    response_english = Column(Text, nullable=True)
    response_translated = Column(Text, nullable=True)
    response_language = Column(String(10), index=True, nullable=True)

  
    translation_service = Column(String(50), nullable=False, default="helsinki")
    translation_success = Column(Boolean, index=True, nullable=False, default=True)
    

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<TranslationRecordModel(ticket_id='{self.ticket_id}', lang='{self.original_language}', success={self.translation_success})>"
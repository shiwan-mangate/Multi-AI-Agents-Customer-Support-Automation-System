from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, text
from crm_agent.db.base import Base

class Escalation(Base):
    __tablename__ = 'escalations'

    escalation_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('escalations_escalation_id_seq'::regclass)")
    )
    
    # Mapped as String(100) to perfectly match the tickets.ticket_id column type
    ticket_id = Column(
        String(100), 
        ForeignKey('tickets.ticket_id', name='escalations_ticket_id_fkey'), 
        nullable=False
    )
    
    # Using Text instead of String for unlimited length as defined in the schema
    reason = Column(Text, nullable=False)
    
    escalated_to = Column(String(100), nullable=True)
    
    # Note: Unlike previous tables, created_at is strictly nullable=True here
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Explicitly defining the index to match 'idx_escalations_ticket_id'
    __table_args__ = (
        Index('idx_escalations_ticket_id', 'ticket_id'),
    )
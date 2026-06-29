from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.schema import UniqueConstraint
from crm_agent.db.base import Base

class Ticket(Base):
    __tablename__ = 'tickets'

    # ticket_id is a String but uses a sequence for its default value.
    # The text() construct perfectly mirrors this exact Postgres behavior.
    ticket_id = Column(
        String(100), 
        primary_key=True, 
        server_default=text("nextval('tickets_ticket_id_seq'::regclass)")
    )
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='tickets_customer_id_fkey'), 
        nullable=False
    )
    
    issue_type = Column(String(100), nullable=False)
    
    sentiment = Column(String(50), nullable=True)
    
    priority = Column(String(50), nullable=True)
    
    resolved = Column(
        Boolean, 
        nullable=True, 
        server_default=text("false")
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    ticket_ref = Column(String(100), nullable=True)

    # Explicitly naming the unique constraint and index prevents Alembic from generating new ones
    __table_args__ = (
        UniqueConstraint('ticket_ref', name='tickets_ticket_ref_key'),
        Index('idx_tickets_customer_id', 'customer_id'),
    )
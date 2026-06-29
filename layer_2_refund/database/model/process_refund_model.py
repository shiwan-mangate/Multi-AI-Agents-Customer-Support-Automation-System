from sqlalchemy import Column, BigInteger, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, text
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class ProcessedRefund(Base):
    __tablename__ = 'processed_refunds'

    id = Column(
        BigInteger, 
        primary_key=True, 
        server_default=text("nextval('processed_refunds_id_seq'::regclass)")
    )
    
    idempotency_key = Column(String(100), nullable=False)
    
    # The foreign key links back to the orders table from the triage agent schema
    order_id = Column(
        Integer, 
        ForeignKey('orders.order_id', name='processed_refunds_order_id_fkey'), 
        nullable=False
    )
    
    refund_status = Column(String(50), nullable=False)
    
    decision_reason = Column(Text, nullable=True)
    
    refund_amount = Column(Numeric(precision=12, scale=2), nullable=True)
    
    requires_human_review = Column(
        Boolean, 
        nullable=True, 
        server_default=text("false")
    )
    
    # Explicitly using the PostgreSQL dialect JSONB type 
    # to prevent Alembic from trying to cast it to a generic JSON or VARCHAR
    metadata_ = Column('metadata', JSONB, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        # Mirroring the exact 'now()' function shown in the schema
        server_default=text("now()")
    )

    # Explicitly naming the unique constraint prevents Alembic drift
    __table_args__ = (
        UniqueConstraint('idempotency_key', name='processed_refunds_idempotency_key_key'),
    )
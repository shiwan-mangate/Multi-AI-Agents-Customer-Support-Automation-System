from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class IdempotencyKey(Base):
    __tablename__ = 'idempotency_keys'

    id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('idempotency_keys_id_seq'::regclass)")
    )
    
    idempotency_key = Column(String(255), nullable=False)
    
    action_type = Column(String(100), nullable=True)
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='idempotency_keys_customer_id_fkey'), 
        nullable=True
    )
    
    status = Column(String(50), nullable=True)
    
    response_payload = Column(JSONB, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )

    __table_args__ = (
        # UPDATED: Full array matching the security audit actions
        CheckConstraint(
            "((action_type)::text = ANY ((ARRAY['password_reset'::character varying, 'account_unlock'::character varying, 'billing_explanation'::character varying, 'invoice_retrieval'::character varying, 'subscription_upgrade'::character varying, 'subscription_downgrade'::character varying, 'subscription_cancel'::character varying, 'subscription_pause'::character varying, 'access_sync'::character varying, 'security_escalation'::character varying])::text[]))", 
            name='idempotency_keys_action_type_check'
        ),
        CheckConstraint(
            "((status)::text = ANY ((ARRAY['processing'::character varying, 'completed'::character varying, 'failed'::character varying])::text[]))", 
            name='idempotency_keys_status_check'
        ),
        UniqueConstraint('idempotency_key', name='idempotency_keys_idempotency_key_key'),
        Index('idx_idempotency_key', 'idempotency_key'),
    )
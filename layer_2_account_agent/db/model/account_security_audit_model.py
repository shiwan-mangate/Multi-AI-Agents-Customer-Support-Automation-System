from sqlalchemy import Column, Integer, BigInteger, String, Numeric, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class AccountSecurityAudit(Base):
    __tablename__ = 'account_security_audit'

    audit_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('account_security_audit_audit_id_seq'::regclass)")
    )
    
    ticket_id = Column(
        String(100), 
        ForeignKey('tickets.ticket_id', name='account_security_audit_ticket_id_fkey'), 
        nullable=True
    )
    
    ticket_ref = Column(String(100), nullable=True)
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='account_security_audit_customer_id_fkey'), 
        nullable=True
    )
    
    workflow_id = Column(String(100), nullable=False)
    
    correlation_id = Column(String(100), nullable=False)
    
    action_type = Column(String(100), nullable=True)
    
    verification_level = Column(String(20), nullable=True)
    
    risk_score = Column(Numeric(precision=5, scale=2), nullable=True)
    
    decision = Column(String(50), nullable=True)
    
    provider_response = Column(JSONB, nullable=True)
    
    operator_type = Column(
        String(20), 
        nullable=True, 
        server_default=text("'AI'::character varying")
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )

    __table_args__ = (
        # UPDATED: Full array with all subscription and escalation events
        CheckConstraint(
            "((action_type)::text = ANY ((ARRAY['password_reset'::character varying, 'account_unlock'::character varying, 'billing_explanation'::character varying, 'invoice_retrieval'::character varying, 'subscription_upgrade'::character varying, 'subscription_downgrade'::character varying, 'subscription_cancel'::character varying, 'subscription_pause'::character varying, 'access_sync'::character varying, 'security_escalation'::character varying])::text[]))", 
            name='account_security_audit_action_type_check'
        ),
        CheckConstraint(
            "((operator_type)::text = ANY ((ARRAY['AI'::character varying, 'HUMAN'::character varying, 'SYSTEM'::character varying])::text[]))", 
            name='account_security_audit_operator_type_check'
        ),
        CheckConstraint(
            "(risk_score >= (0)::numeric)", 
            name='account_security_audit_risk_score_check'
        ),
        CheckConstraint(
            "((verification_level)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'FAILED'::character varying])::text[]))", 
            name='account_security_audit_verification_level_check'
        ),
        Index('idx_security_audit_customer', 'customer_id'),
        Index('idx_security_audit_ticket', 'ticket_id'),
    )
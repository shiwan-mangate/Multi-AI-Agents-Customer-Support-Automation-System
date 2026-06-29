from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class EscalationAudit(Base):
    __tablename__ = 'escalation_audit'

    audit_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('escalation_audit_audit_id_seq'::regclass)")
    )
    
    # Note the explicit ondelete='CASCADE' mirroring the database definition
    case_id = Column(
        String(100), 
        ForeignKey('escalation_cases.case_id', name='escalation_audit_case_id_fkey', ondelete='CASCADE'), 
        nullable=False
    )
    
    ticket_id = Column(String(100), nullable=True)
    
    event_type = Column(String(100), nullable=False)
    
    payload = Column(JSONB, nullable=True)
    
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
        # 1. Event Type Check Constraint (Perfect sync with the live database)
        CheckConstraint(
            "((event_type)::text = ANY ((ARRAY['trigger_detected'::character varying, 'duplicate_detected'::character varying, 'risk_scored'::character varying, 'holding_sent'::character varying, 'brief_generated'::character varying, 'routing_completed'::character varying, 'notification_enqueued'::character varying, 'case_resolved'::character varying, 'case_closed'::character varying, 'error'::character varying])::text[]))", 
            name='escalation_audit_event_type_check'
        ),
        
        # 2. Operator Type Check Constraint
        CheckConstraint(
            "((operator_type)::text = ANY ((ARRAY['AI'::character varying, 'HUMAN'::character varying, 'SYSTEM'::character varying])::text[]))", 
            name='escalation_audit_operator_type_check'
        ),
        
        # 3. Standard Index Mapping
        Index('idx_escalation_audit_case', 'case_id'),
    )
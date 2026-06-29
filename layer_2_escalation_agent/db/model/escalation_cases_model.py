from sqlalchemy import Column, BigInteger, String, Text, Numeric, Boolean, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class EscalationCase(Base):
    __tablename__ = 'escalation_cases'

    case_id = Column(String(100), primary_key=True)
    
    ticket_id = Column(String(100), nullable=False)
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='escalation_cases_customer_id_fkey'), 
        nullable=False
    )
    
    source_agent = Column(String(50), nullable=False)
    
    trigger_category = Column(String(50), nullable=False)
    
    trigger_reasons = Column(JSONB, nullable=False)
    
    risk_score = Column(Numeric(precision=5, scale=2), nullable=True)
    
    risk_level = Column(String(20), nullable=True)
    
    assigned_team = Column(String(100), nullable=True)
    
    status = Column(String(50), nullable=False)
    
    holding_sent = Column(Boolean, nullable=True, server_default=text("false"))
    
    holding_message = Column(Text, nullable=True)
    
    human_brief = Column(JSONB, nullable=True)
    
    recommended_action = Column(Text, nullable=True)
    
    sla_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Self-referencing Foreign Key with ON DELETE SET NULL
    duplicate_of_case_id = Column(
        String(100), 
        ForeignKey('escalation_cases.case_id', name='escalation_cases_duplicate_of_case_id_fkey', ondelete='SET NULL'), 
        nullable=True
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )
    
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "((risk_level)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'URGENT'::character varying])::text[]))", 
            name='escalation_cases_risk_level_check'
        ),
        CheckConstraint(
            "(risk_score >= (0)::numeric)", 
            name='escalation_cases_risk_score_check'
        ),
        # UPDATED: Full array including 'system' and 'supervisor'
        CheckConstraint(
            "((source_agent)::text = ANY ((ARRAY['triage_agent'::character varying, 'refund_agent'::character varying, 'account_agent'::character varying, 'faq_agent'::character varying, 'proactive_agent'::character varying, 'system'::character varying, 'supervisor'::character varying])::text[]))", 
            name='escalation_cases_source_agent_check'
        ),
        CheckConstraint(
            "((status)::text = ANY ((ARRAY['open'::character varying, 'in_review'::character varying, 'resolved'::character varying, 'closed'::character varying])::text[]))", 
            name='escalation_cases_status_check'
        ),
        # UPDATED: Full array including 'manual_review', 'repeat_issue', etc.
        CheckConstraint(
            "((trigger_category)::text = ANY ((ARRAY['legal'::character varying, 'security'::character varying, 'churn'::character varying, 'sla'::character varying, 'knowledge_gap'::character varying, 'manual_review'::character varying, 'repeat_issue'::character varying, 'operational'::character varying, 'general'::character varying])::text[]))", 
            name='escalation_cases_trigger_category_check'
        ),
        Index('idx_escalation_cases_status', 'status'),
        Index('idx_escalation_cases_sla', 'sla_deadline'),
        Index('idx_escalation_cases_ticket', 'ticket_id'),
        Index('idx_escalation_cases_customer', 'customer_id'),
    )
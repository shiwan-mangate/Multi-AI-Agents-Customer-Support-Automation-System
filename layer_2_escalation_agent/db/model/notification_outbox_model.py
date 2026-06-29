from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from crm_agent.db.base import Base

class NotificationOutbox(Base):
    __tablename__ = 'notification_outbox'

    id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('notification_outbox_id_seq'::regclass)")
    )
    
    case_id = Column(
        String(100), 
        ForeignKey('escalation_cases.case_id', name='notification_outbox_case_id_fkey', ondelete='CASCADE'), 
        nullable=False
    )
    
    channel = Column(String(50), nullable=True)
    
    recipient = Column(String(255), nullable=True)
    
    payload = Column(JSONB, nullable=False)
    
    status = Column(
        String(50), 
        nullable=True, 
        server_default=text("'pending'::character varying")
    )
    
    retry_count = Column(
        Integer, 
        nullable=True, 
        server_default=text("0")
    )
    
    last_error = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )
    
    processed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "((channel)::text = ANY ((ARRAY['dashboard'::character varying, 'email'::character varying, 'slack'::character varying, 'telegram'::character varying, 'pager'::character varying])::text[]))", 
            name='notification_outbox_channel_check'
        ),
        CheckConstraint(
            "(retry_count >= 0)", 
            name='notification_outbox_retry_count_check'
        ),
        CheckConstraint(
            "((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'sent'::character varying, 'failed'::character varying])::text[]))", 
            name='notification_outbox_status_check'
        ),
        Index('idx_notification_outbox_status', 'status'),
    )
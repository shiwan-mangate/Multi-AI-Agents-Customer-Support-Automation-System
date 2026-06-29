from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Index, CheckConstraint, text
from crm_agent.db.base import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('subscriptions_subscription_id_seq'::regclass)")
    )
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='subscriptions_customer_id_fkey'), 
        nullable=False
    )
    
    plan_name = Column(String(100), nullable=False)
    
    billing_cycle = Column(String(20), nullable=False)
    
    status = Column(String(50), nullable=False)
    
    auto_renew = Column(Boolean, nullable=True, server_default=text("true"))
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    
    renews_at = Column(DateTime(timezone=True), nullable=True)
    
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )

    __table_args__ = (
        # 1. Exact match for the billing_cycle check constraint array
        CheckConstraint(
            "((billing_cycle)::text = ANY ((ARRAY['monthly'::character varying, 'yearly'::character varying])::text[]))", 
            name='subscriptions_billing_cycle_check'
        ),
        
        # 2. Exact match for the status check constraint array
        CheckConstraint(
            "((status)::text = ANY ((ARRAY['active'::character varying, 'paused'::character varying, 'cancelled'::character varying, 'trial'::character varying, 'past_due'::character varying])::text[]))", 
            name='subscriptions_status_check'
        ),
        
        # 3. Explicit index naming to prevent Alembic drift
        Index('idx_subscriptions_customer', 'customer_id'),
    )
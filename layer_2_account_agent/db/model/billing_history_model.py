from sqlalchemy import Column, Integer, BigInteger, String, Numeric, DateTime, ForeignKey, Index, CheckConstraint, text
from crm_agent.db.base import Base

class BillingHistory(Base):
    __tablename__ = 'billing_history'

    billing_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('billing_history_billing_id_seq'::regclass)")
    )
    
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='billing_history_customer_id_fkey'), 
        nullable=False
    )
    
    subscription_id = Column(
        Integer, 
        ForeignKey('subscriptions.subscription_id', name='billing_history_subscription_id_fkey'), 
        nullable=True
    )
    
    invoice_id = Column(String(100), nullable=True)
    
    charge_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    
    currency = Column(
        String(10), 
        nullable=True, 
        server_default=text("'USD'::character varying")
    )
    
    charge_type = Column(String(50), nullable=True)
    
    status = Column(String(50), nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint(
            "(charge_amount >= (0)::numeric)", 
            name='billing_history_charge_amount_check'
        ),
        # UPDATED: Full array including 'manual_adjustment'
        CheckConstraint(
            "((charge_type)::text = ANY ((ARRAY['renewal'::character varying, 'upgrade'::character varying, 'downgrade'::character varying, 'invoice'::character varying, 'failed_payment'::character varying, 'manual_adjustment'::character varying])::text[]))", 
            name='billing_history_charge_type_check'
        ),
        CheckConstraint(
            "((status)::text = ANY ((ARRAY['paid'::character varying, 'failed'::character varying, 'pending'::character varying, 'refunded'::character varying])::text[]))", 
            name='billing_history_status_check'
        ),
        Index('idx_billing_customer', 'customer_id'),
        Index('idx_billing_subscription', 'subscription_id'),
    )
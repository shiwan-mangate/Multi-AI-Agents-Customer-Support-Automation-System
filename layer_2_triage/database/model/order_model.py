from sqlalchemy import Column, Integer, BigInteger, String, Numeric, DateTime, ForeignKey, Index, text
from crm_agent.db.base import Base

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(
        Integer, 
        primary_key=True, 
    
        server_default=text("nextval('orders_order_id_seq'::regclass)")
    )
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='orders_customer_id_fkey'), 
        nullable=False
    )
    order_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    order_status = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )

   
    __table_args__ = (
        Index('idx_orders_customer_id', 'customer_id'),
    )

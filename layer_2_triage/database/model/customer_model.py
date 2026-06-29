from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, text
from sqlalchemy.schema import UniqueConstraint
from crm_agent.db.base import Base

class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(
        BigInteger, 
        primary_key=True, 
        server_default=text("nextval('customers_customer_id_seq'::regclass)")
    )
    name = Column(String(100), nullable=False)
    
    # Removed unique=True from here to avoid Alembic duplication
    email = Column(String(150), nullable=False) 
    
    account_tier = Column(
        String(50), 
        nullable=True, 
        server_default=text("'standard'::character varying")
    )
    
    total_spent = Column(
        Numeric(precision=10, scale=2), 
        nullable=True, 
        server_default=text("0.00")
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Explicitly named constraint ensures Alembic parity
    __table_args__ = (
        UniqueConstraint('email', name='customers_email_key'),
    )
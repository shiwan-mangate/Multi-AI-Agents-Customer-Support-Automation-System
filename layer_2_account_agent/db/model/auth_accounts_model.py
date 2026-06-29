from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.schema import UniqueConstraint
from crm_agent.db.base import Base

class AuthAccount(Base):
    __tablename__ = 'auth_accounts'

    auth_account_id = Column(
        Integer, 
        primary_key=True, 
        server_default=text("nextval('auth_accounts_auth_account_id_seq'::regclass)")
    )
    
    # Links back to the unified customers table
    customer_id = Column(
        BigInteger, 
        ForeignKey('customers.customer_id', name='auth_accounts_customer_id_fkey'), 
        nullable=False
    )
    
    login_provider = Column(
        String(50), 
        nullable=True, 
        server_default=text("'local'::character varying")
    )
    
    account_locked = Column(Boolean, nullable=True, server_default=text("false"))
    
    failed_login_attempts = Column(Integer, nullable=True, server_default=text("0"))
    
    two_factor_enabled = Column(Boolean, nullable=True, server_default=text("false"))
    
    suspicious_flag = Column(Boolean, nullable=True, server_default=text("false"))
    
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    last_password_reset_at = Column(DateTime(timezone=True), nullable=True)
    
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

    __table_args__ = (
        # 1. Exact match for the numeric check constraint
        CheckConstraint(
            '(failed_login_attempts >= 0)', 
            name='auth_accounts_failed_login_attempts_check'
        ),
        
        # 2. Exact match for the heavily casted array check constraint
        # Postgres is extremely strict about the text representation of arrays and type casts.
        # This string perfectly mirrors the database's internal memory state.
        CheckConstraint(
            "((login_provider)::text = ANY ((ARRAY['local'::character varying, 'google'::character varying, 'github'::character varying, 'sso'::character varying])::text[]))", 
            name='auth_accounts_login_provider_check'
        ),
        
        # 3. Explicitly capturing the Unique Constraint
        UniqueConstraint('customer_id', name='auth_accounts_customer_id_key'),
        
        # 4. Explicitly capturing the standard Index
        # Note: Your DB has both a Unique constraint AND a standard index on the exact same column (customer_id).
        # We must define both here so Alembic doesn't attempt to drop the "redundant" one.
        Index('idx_auth_accounts_customer', 'customer_id'),
    )
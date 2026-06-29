from typing import Union
from sqlalchemy.orm import Session
from crm_agent.db.connection import SessionLocal

# Importing the exact-match model we created previously
from layer_2_triage.database.model.order_model import Order

class OrderRepository:
    def __init__(self, db: Session = None):
        # Uses the injected session or creates a new one from the local factory
        self.db = db or SessionLocal()

    def get_order_by_id(self, order_id: Union[str, int]):
        """
        Fetches order details. 
        Aligned with PostgreSQL schema:
        - order_id: integer
        - customer_id: bigint
        - order_amount: numeric
        - order_status: character varying
        - created_at: timestamp with time zone
        """
        # Explicit column selection to mirror the raw SQL SELECT statement exactly
        result = self.db.query(
            Order.order_id,
            Order.customer_id,
            Order.order_amount,
            Order.order_status,
            Order.created_at
        ).filter(
            Order.order_id == order_id
        ).first()
        
        # _asdict() cleanly replaces dict(result._mapping) while preserving return format
        return result._asdict() if result else None

    def close(self):
        """Returns the connection to the SQLAlchemy pool."""
        self.db.close()
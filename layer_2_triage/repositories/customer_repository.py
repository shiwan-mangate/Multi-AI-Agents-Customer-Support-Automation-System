from sqlalchemy.orm import Session
from sqlalchemy import func
from crm_agent.db.connection import SessionLocal

# Importing the exact-match models we created
from layer_2_triage.database.model.customer_model import Customer
from layer_2_triage.database.model.ticket_model import Ticket
from layer_2_triage.database.model.escalation_model import Escalation

class CustomerRepository:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def get_customer_by_id(self, customer_id: int):
        """Standard fetch for basic profile data."""
        # Querying specific columns equivalent to the explicit SELECT statement
        result = self.db.query(
            Customer.customer_id, 
            Customer.name, 
            Customer.email, 
            Customer.account_tier, 
            Customer.total_spent
        ).filter(
            Customer.customer_id == customer_id
        ).first()
        
        # _asdict() seamlessly replaces dict(result._mapping)
        return result._asdict() if result else None
    
    def get_customer_by_email(self, email: str):
        """
        Resolves customer identity from email.
        Used by fetch_customer_node as the primary workflow lookup.
        """
        result = self.db.query(
            Customer.customer_id, 
            Customer.name, 
            Customer.email, 
            Customer.account_tier, 
            Customer.total_spent
        ).filter(
            Customer.email == email
        ).first()

        return result._asdict() if result else None
    
    def get_triage_context(self, customer_id: int):
        """
        Fetches profile, LTV, and history count 
        in a single query to minimize DB latency.
        """
        # Mapping the explicit SELECT, LEFT JOIN, and GROUP BY logic
        result = self.db.query(
            Customer.customer_id,
            Customer.name,
            Customer.account_tier,
            Customer.total_spent.label('ltv'),
            func.count(func.distinct(Ticket.ticket_id)).label('total_tickets'),
            func.count(func.distinct(Escalation.escalation_id)).label('total_escalations')
        ).outerjoin(
            # LEFT JOIN tickets t ON c.customer_id = t.customer_id
            Ticket, Customer.customer_id == Ticket.customer_id
        ).outerjoin(
            # LEFT JOIN escalations e ON t.ticket_id = e.ticket_id
            Escalation, Ticket.ticket_id == Escalation.ticket_id
        ).filter(
            Customer.customer_id == customer_id
        ).group_by(
            Customer.customer_id, 
            Customer.name, 
            Customer.account_tier, 
            Customer.total_spent
        ).first()
        
        return result._asdict() if result else None

    def close(self):
        """Closes the session to return the connection to the pool."""
        self.db.close()
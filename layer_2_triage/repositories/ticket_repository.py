from sqlalchemy.orm import Session
from sqlalchemy import func, text
from crm_agent.db.connection import SessionLocal
from layer_2_triage.database.model.ticket_model import Ticket

class TicketRepository:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def count_unresolved_repeat_issues(self, customer_id: int, category: str):
        """
        Detects UNRESOLVED patterns. 
        Schema check: 'issue_type', 'resolved', and 'created_at' match DB exactly.
        """
        return self.db.query(func.count(Ticket.ticket_id)).filter(
            Ticket.customer_id == customer_id,
            Ticket.issue_type == category,
            Ticket.resolved == False,
            # Utilizing func.now() and text() to preserve strict DB-side evaluation
            Ticket.created_at >= func.now() - text("INTERVAL '30 days'")
        ).scalar()

    def get_recent_ticket_count(self, customer_id: int, days: int = 7):
        """
        Returns raw count for spike detection. 
        """
        return self.db.query(func.count(Ticket.ticket_id)).filter(
            Ticket.customer_id == customer_id,
            # Safely casting the integer to maintain the identical Postgres CAST interval logic
            Ticket.created_at >= func.now() - text(f"INTERVAL '{int(days)} days'")
        ).scalar()

    def get_last_ticket_sentiment(self, customer_id: int):
        """
        Retrieves the most recent sentiment to calculate sentiment multipliers.
        Schema check: 'sentiment' is a character varying column.
        """
        return self.db.query(Ticket.sentiment).filter(
            Ticket.customer_id == customer_id
        ).order_by(
            Ticket.created_at.desc()
        ).scalar()

    def get_previous_ticket_count(self, customer_id: int) -> int:
        """
        Get all the previous ticket count of the customer.
        """
        return self.db.query(func.count(Ticket.ticket_id)).filter(
            Ticket.customer_id == customer_id
        ).scalar()

    def close(self):
        """Closes the session to return the connection to the pool."""
        self.db.close()
import logging
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

# Importing the core Ticket model from the Triage Agent
from layer_2_triage.database.model.ticket_model import Ticket

logger = logging.getLogger(__name__)

class TicketRepository:
    """
    Shared ticket intelligence repository.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _sanitize_limit(limit: int) -> int:
        return max(1, min(limit, 50))

    def _base_query(self):
        """Helper to ensure consistent column selection across ticket fetches."""
        return self.session.query(
            Ticket.ticket_id,
            Ticket.customer_id,
            Ticket.issue_type,
            Ticket.ticket_ref,
            Ticket.sentiment,
            Ticket.priority,
            Ticket.resolved,
            Ticket.created_at
        )

    def get_ticket_by_id(
        self,
        ticket_id: str 
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch current ticket context.
        """
        try:
            result = self._base_query().filter(
                Ticket.ticket_id == str(ticket_id)
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching ticket_id=%s",
                ticket_id
            )
            return None

    def get_recent_tickets(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent ticket history.
        """
        limit = self._sanitize_limit(limit)

        try:
            results = self._base_query().filter(
                Ticket.customer_id == customer_id
            ).order_by(
                Ticket.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching recent tickets customer_id=%s",
                customer_id
            )
            return []

    def count_repeat_issues(self, customer_id: int, issue_type: Optional[str] = None) -> int:
        
        try:
            query = self.session.query(func.count(Ticket.ticket_id)).filter(
                Ticket.customer_id == customer_id
            )

            # Refactored: Mapped 'intent' from the original raw SQL to 'issue_type'
            if issue_type:
                query = query.filter(Ticket.issue_type == issue_type)

            result = query.scalar()
            return int(result) if result else 0

        except Exception:
            logger.exception("Failed counting repeat issues for customer_id=%s", customer_id)
            return 0

    def count_unresolved_tickets(
        self,
        customer_id: int
    ) -> int:
        """
        Count unresolved/open complaints.
        """
        try:
            result = self.session.query(func.count(Ticket.ticket_id)).filter(
                Ticket.customer_id == customer_id,
                Ticket.resolved == False
            ).scalar()

            return int(result) if result else 0

        except Exception:
            logger.exception(
                "Failed counting unresolved tickets customer_id=%s",
                customer_id
            )
            return 0

    def get_previous_ticket_count(self, customer_id: int) -> int:
        
        try:
            result = self.session.query(func.count(Ticket.ticket_id)).filter(
                Ticket.customer_id == customer_id
            ).scalar()
            
            return int(result) if result else 0

        except Exception:
            logger.exception("Failed fetching previous ticket count for customer_id=%s", customer_id)
            return 0

    def get_last_ticket_sentiment(
        self,
        customer_id: int
    ) -> Optional[str]:
        """
        Fetch most recent customer sentiment.
        """
        try:
            result = self.session.query(Ticket.sentiment).filter(
                Ticket.customer_id == customer_id
            ).order_by(
                Ticket.created_at.desc()
            ).first()

            # result is a tuple like ('negative',), so we extract the first element
            return str(result[0]) if result and result[0] else None

        except Exception:
            logger.exception(
                "Failed fetching sentiment customer_id=%s",
                customer_id
            )
            return None
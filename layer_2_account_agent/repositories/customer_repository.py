from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

# Importing the central models we created during the Triage Agent refactoring
from layer_2_triage.database.model.customer_model import Customer
from layer_2_triage.database.model.order_model import Order
from layer_2_triage.database.model.ticket_model import Ticket
from layer_2_triage.database.model.escalation_model import Escalation

logger = logging.getLogger(__name__)

class CustomerRepository:
    """
    Repository for customer CRM, transactional history,
    and behavioral intelligence.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _sanitize_limit(limit: int) -> int:
        return max(1, min(limit, 50))

    def _customer_query(self):
        """
        Helper method to mirror the original CUSTOMER_COLUMNS string.
        """
        return self.session.query(
            Customer.customer_id,
            Customer.name,
            Customer.email,
            Customer.account_tier,
            Customer.total_spent,
            Customer.created_at
        )

    def get_customer_by_email(self, email: Optional[str]) -> Optional[Dict[str, Any]]:
        
        if not email:
            return None

        try:
            result = self._customer_query().filter(
                Customer.email == email
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch customer by email: %s",
                email
            )
            return None

    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        
        try:
            result = self._customer_query().filter(
                Customer.customer_id == customer_id
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch customer by id: %s",
                customer_id
            )
            return None

    def get_recent_orders(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        
        limit = self._sanitize_limit(limit)

        try:
            results = self.session.query(
                Order.order_id,
                Order.order_amount,
                Order.order_status,
                Order.created_at
            ).filter(
                Order.customer_id == customer_id
            ).order_by(
                Order.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed to fetch orders for customer: %s",
                customer_id
            )
            return []

    def get_ticket_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        
        limit = self._sanitize_limit(limit)

        try:
            results = self.session.query(
                Ticket.ticket_id,
                Ticket.ticket_ref,
                Ticket.issue_type,
                Ticket.sentiment,
                Ticket.priority,
                Ticket.resolved,
                Ticket.created_at
            ).filter(
                Ticket.customer_id == customer_id
            ).order_by(
                Ticket.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed to fetch tickets for customer: %s",
                customer_id
            )
            return []

    def get_escalation_history(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        
        limit = self._sanitize_limit(limit)

        try:
            # Replicating the JOIN across escalations and tickets
            results = self.session.query(
                Escalation.escalation_id,
                Escalation.reason,
                Escalation.escalated_to,
                Escalation.created_at,
                Ticket.ticket_id,
                Ticket.ticket_ref,
                Ticket.issue_type
            ).join(
                # JOIN tickets t ON e.ticket_id = t.ticket_id
                Ticket, Escalation.ticket_id == Ticket.ticket_id
            ).filter(
                # WHERE t.customer_id = :customer_id
                Ticket.customer_id == customer_id
            ).order_by(
                Escalation.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed to fetch escalation history for customer: %s",
                customer_id
            )
            return []
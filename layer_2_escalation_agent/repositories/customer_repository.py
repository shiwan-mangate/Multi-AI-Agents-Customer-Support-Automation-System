import logging
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

# Core Agent Imports across domains
from layer_2_triage.database.model.customer_model import Customer
from layer_2_triage.database.model.order_model import Order
from layer_2_account_agent.db.model.subscriptions_model import Subscription
from layer_2_escalation_agent.db.model.escalation_cases_model import EscalationCase
from crm_agent.db.models.customer_profile_model import CustomerProfile

logger = logging.getLogger(__name__)

class CustomerRepository:
    """
    Shared customer intelligence repository.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _sanitize_limit(limit: int) -> int:
        return max(1, min(limit, 50))

    def _base_customer_query(self):
        """Helper for consistent customer SELECT fields"""
        return self.session.query(
            Customer.customer_id,
            Customer.name,
            Customer.email,
            Customer.account_tier,
            Customer.total_spent,
            Customer.created_at
        )

    def get_customer_by_id(
        self,
        customer_id: int
    ) -> Optional[Dict[str, Any]]:
        
        try:
            result = self._base_customer_query().filter(
                Customer.customer_id == customer_id
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching customer id=%s",
                customer_id
            )
            return None

    def get_customer_by_email(
        self,
        email: str
    ) -> Optional[Dict[str, Any]]:
        
        try:
            result = self._base_customer_query().filter(
                Customer.email == email
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching customer email=%s",
                email
            )
            return None

    def get_customer_subscription(
        self,
        customer_id: int
    ) -> Optional[Dict[str, Any]]:
        
        try:
            result = self.session.query(
                Subscription.plan_name,
                Subscription.status
            ).filter(
                Subscription.customer_id == customer_id
            ).order_by(
                Subscription.created_at.desc()
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching subscription customer_id=%s",
                customer_id
            )
            return None

    def get_billing_history(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch customer purchase/billing context from the orders table.
        """
        limit = self._sanitize_limit(limit)

        try:
            results = self.session.query(
                Order.order_id,
                Order.customer_id,
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
                "Failed fetching billing history (orders) customer_id=%s",
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
            # *EscalationCase.__table__.columns natively mimics SELECT *
            results = self.session.query(*EscalationCase.__table__.columns).filter(
                EscalationCase.customer_id == customer_id
            ).order_by(
                EscalationCase.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching escalation history customer_id=%s",
                customer_id
            )
            return []

    def get_customer_risk_profile(
        self,
        customer_id: int
    ) -> Optional[Dict[str, Any]]:
        
        try:
            # Fully converted to ORM using the specific schema columns requested
            result = self.session.query(
                CustomerProfile.customer_id,
                CustomerProfile.negative_ticket_count,
                CustomerProfile.repeat_negative_count,
                CustomerProfile.repeat_escalation_count,
                CustomerProfile.total_failures,
                CustomerProfile.total_escalations,
                CustomerProfile.churn_score,
                CustomerProfile.churn_level,
                CustomerProfile.last_sentiment
            ).filter(
                CustomerProfile.customer_id == customer_id
            ).first()

            return result._asdict() if result else None
            
        except Exception:
            logger.exception(
                "Failed fetching customer risk profile customer_id=%s",
                customer_id
            )
            return None
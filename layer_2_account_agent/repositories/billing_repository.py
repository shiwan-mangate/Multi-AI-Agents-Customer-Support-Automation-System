from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

# Import the exact BillingHistory model we generated for the Account Agent
from layer_2_account_agent.db.model.billing_history_model import BillingHistory

logger = logging.getLogger(__name__)

class BillingRepository:
    """
    Read-only repository for customer billing intelligence.

    Responsibilities:
    - billing history lookup
    - invoice retrieval
    - failed payment diagnostics
    - latest billing context retrieval
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _sanitize_limit(limit: int) -> int:
        """
        Prevent abusive / invalid query limits.
        """
        return max(1, min(limit, 50))

    def _base_query(self):
        """
        Helper method to mirror the original BILLING_COLUMNS string.
        Selects specific columns to ensure lightweight, consistent dictionary returns.
        """
        return self.session.query(
            BillingHistory.billing_id,
            BillingHistory.customer_id,
            BillingHistory.subscription_id,
            BillingHistory.invoice_id,
            BillingHistory.charge_amount,
            BillingHistory.currency,
            BillingHistory.charge_type,
            BillingHistory.status,
            BillingHistory.created_at
        )

    def get_billing_history(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent billing transactions.

        Useful for:
        - billing explanation workflows
        - customer charge review
        - diagnosing past_due subscriptions
        """
        if not customer_id:
            return []

        limit = self._sanitize_limit(limit)

        try:
            results = self._base_query().filter(
                BillingHistory.customer_id == customer_id
            ).order_by(
                BillingHistory.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed to fetch billing history for customer_id=%s",
                customer_id
            )
            return []

    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific invoice by invoice reference.
        """
        if not invoice_id:
            return None

        try:
            result = self._base_query().filter(
                BillingHistory.invoice_id == invoice_id
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch invoice invoice_id=%s",
                invoice_id
            )
            return None

    def get_latest_invoice(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest billing record for a customer.

        Useful when customer says:
        'Why was I charged?'
        but provides no invoice ID.
        """
        if not customer_id:
            return None

        try:
            result = self._base_query().filter(
                BillingHistory.customer_id == customer_id
            ).order_by(
                BillingHistory.created_at.desc()
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch latest invoice for customer_id=%s",
                customer_id
            )
            return None

    def get_failed_payments(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch failed payment records.

        Useful for:
        - subscription past_due diagnosis
        - payment troubleshooting
        """
        if not customer_id:
            return []

        limit = self._sanitize_limit(limit)

        try:
            results = self._base_query().filter(
                BillingHistory.customer_id == customer_id,
                BillingHistory.status == 'failed'
            ).order_by(
                BillingHistory.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed to fetch failed payments for customer_id=%s",
                customer_id
            )
            return []
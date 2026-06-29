import logging
from typing import Optional

from sqlalchemy.orm import Session

from layer_2_refund.repositories.base_repository import (
    AbstractCustomerRepository
)

from layer_2_refund.schemas.refund_models import (
    CustomerData
)

from layer_2_triage.database.model.customer_model import Customer

logger = logging.getLogger(__name__)

class CustomerRepository(AbstractCustomerRepository):

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def get_customer_by_id(
        self,
        customer_id: int
    ) -> Optional[CustomerData]:

        try:
            # ORM Query equivalent to SELECT ... WHERE customer_id = :customer_id
            customer = self.session.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()

            if not customer:
                return None

            # ALIGNED: Safe float parsing for nullable fields preserved exactly
            raw_total_spent = customer.total_spent
            safe_total_spent = float(raw_total_spent) if raw_total_spent is not None else 0.0

            return CustomerData(
                customer_id=customer.customer_id,
                name=customer.name,
                email=customer.email,
                total_spent=safe_total_spent,
                # Using standard fallback if the DB value is somehow null
                account_tier=customer.account_tier if customer.account_tier else "standard",
                created_at=customer.created_at
            )

        except Exception:
            self.session.rollback()

            logger.exception(
                "Failed fetching customer_id=%s",
                customer_id
            )

            return None

    def update_customer_after_refund(
        self,
        customer_id: int,
        new_total_spent: float
    ) -> bool:

        try:
            # ORM equivalent to the UPDATE ... SET ... WHERE ...
            # Using .update() performs this efficiently at the DB level
            rowcount = self.session.query(Customer).filter(
                Customer.customer_id == customer_id
            ).update({"total_spent": new_total_spent})

            self.session.commit()

            return rowcount > 0

        except Exception:
            self.session.rollback()

            logger.exception(
                "Failed updating customer_id=%s",
                customer_id
            )

            return False
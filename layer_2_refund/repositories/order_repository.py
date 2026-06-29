import logging
from typing import Optional

from sqlalchemy.orm import Session

from layer_2_refund.repositories.base_repository import (
    AbstractOrderRepository
)

from layer_2_refund.schemas.refund_models import (
    OrderStatus,
    OrderData
)

# Importing the exact Order model we created during the triage agent refactoring
from layer_2_triage.database.model.order_model import Order

logger = logging.getLogger(__name__)

class OrderRepository(
    AbstractOrderRepository
):

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def get_order_by_id(
        self,
        order_id: int
    ) -> Optional[OrderData]:

        try:
            # ORM query equivalent to SELECT ... WHERE order_id = :order_id
            order = self.session.query(Order).filter(
                Order.order_id == order_id
            ).first()

            if not order:
                return None
            
            # Mapping ORM object attributes directly to the Pydantic schema
            return OrderData(
                order_id=order.order_id,
                customer_id=order.customer_id,
                order_amount=float(order.order_amount),
                order_status=OrderStatus(str(order.order_status).upper()),
                created_at=order.created_at,
                is_refundable=None  
            )

        except Exception:

            self.session.rollback()

            logger.exception(
                "Failed fetching order_id=%s",
                order_id
            )

            return None

    def update_order_status(
        self,
        order_id: int,
        status: OrderStatus
    ) -> bool:

        try:
            # Natively executes the UPDATE query and returns the affected rowcount
            rowcount = self.session.query(Order).filter(
                Order.order_id == order_id
            ).update({
                "order_status": status.value
            })

            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise

            return rowcount > 0

        except Exception:

            self.session.rollback()

            logger.exception(
                "Failed updating order_id=%s",
                order_id
            )

            return False
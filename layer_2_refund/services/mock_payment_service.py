import uuid
import logging

from layer_2_refund.schemas.refund_models import (
    RefundExecutionResult
)

logger = logging.getLogger(__name__)


class MockPaymentService:

    def execute_refund(
        self,
        order_id: int,
        amount: float
    ) -> RefundExecutionResult:

        logger.info(
            f"Payment Service | "
            f"Status=STARTING | "
            f"Order={order_id} | "
            f"Amount={amount}"
        )

        if amount <= 0:

            return RefundExecutionResult(
                success=False,
                execution_message=(
                    "Invalid refund amount."
                )
            )

        if amount > 10000:

            return RefundExecutionResult(
                success=False,
                execution_message=(
                    "Amount exceeds automated "
                    "processing limit."
                )
            )

        transaction_id = (
            f"TXN-{uuid.uuid4().hex[:8].upper()}"
        )

        logger.info(
            f"Payment Service | "
            f"Status=SUCCESS | "
            f"Order={order_id} | "
            f"TxnID={transaction_id}"
        )

        return RefundExecutionResult(
            success=True,
            transaction_id=transaction_id,
            execution_message=(
                "Refund successful via MockStripe."
            )
        )
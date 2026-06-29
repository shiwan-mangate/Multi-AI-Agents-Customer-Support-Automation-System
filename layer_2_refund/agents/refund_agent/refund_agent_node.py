## layer_2_refund/agents/refund_agent/refund_agent_node.py
import logging
from typing import Optional

from layer_2_refund.repositories.order_repository import SQLiteOrderRepository
from layer_2_refund.repositories.customer_repository import SQLiteCustomerRepository
from layer_2_refund.repositories.refund_repository import SQLiteRefundRepository

from layer_2_refund.services.mock_payment_service import MockPaymentService

from layer_2_refund.schemas.refund_models import (
    RefundRequest,
    PolicyDecision,
    RefundStatus
)

from layer_2_refund.agents.refund_agent.policy_engine import evaluate_refund


logger = logging.getLogger(__name__)


class RefundAgentNode:

    def __init__(
        self,
        order_repo: SQLiteOrderRepository,
        customer_repo: SQLiteCustomerRepository,
        refund_repo: SQLiteRefundRepository,
        payment_service: MockPaymentService
    ):

        self.order_repo = order_repo
        self.customer_repo = customer_repo
        self.refund_repo = refund_repo
        self.payment_service = payment_service

    def process_refund_request(
        self,
        request: RefundRequest,
        idempotency_key: str
    ) -> PolicyDecision:

        context = (
            f"[Ticket: {request.ticket_id} | "
            f"Order: {request.order_id} | "
            f"Key: {idempotency_key}]"
        )

        try:

            logger.info(f"{context} Starting refund workflow.")

            # ==========================================================
            # 1. TRUE IDEMPOTENCY REPLAY
            # ==========================================================

            previous_decision = (
                self.refund_repo.get_previous_decision(
                    idempotency_key
                )
            )

            if previous_decision is not None:

                logger.info(
                    f"{context} "
                    f"Idempotency hit. Returning cached result."
                )

                return previous_decision

            # ==========================================================
            # 2. FETCH ORDER
            # ==========================================================

            order = self.order_repo.get_order_by_id(
                request.order_id
            )

            if order is None:

                logger.warning(
                    f"{context} Order not found."
                )

                return PolicyDecision(
                    status=RefundStatus.REJECTED,
                    code="ORDER_NOT_FOUND",
                    reason=(
                        "The provided order ID "
                        "does not exist."
                    ),
                    metadata={}
                )

            # ==========================================================
            # 3. FETCH CUSTOMER
            # ==========================================================

            customer = self.customer_repo.get_customer_by_id(
                order.customer_id
            )

            if customer is None:

                logger.error(
                    f"{context} Customer profile missing."
                )

                return PolicyDecision(
                    status=RefundStatus.REJECTED,
                    code="CUSTOMER_NOT_FOUND",
                    reason=(
                        "Customer profile associated "
                        "with the order is missing."
                    ),
                    metadata={}
                )

            # ==========================================================
            # 4. POLICY EVALUATION
            # ==========================================================

            logger.info(
                f"{context} Running policy engine."
            )

            decision = evaluate_refund(
                order,
                customer
            )

            # ==========================================================
            # 5. EXECUTION LAYER
            # ==========================================================

            if decision.status == RefundStatus.APPROVED:

                logger.info(
                    f"{context} "
                    f"Refund approved. "
                    f"Triggering payment execution."
                )

                execution_result = (
                    self.payment_service.execute_refund(
                        order_id=order.order_id,
                        amount=decision.refund_amount
                    )
                )

                # ------------------------------------------------------
                # EXECUTION SUCCESS
                # ------------------------------------------------------

                if execution_result.success:

                    logger.info(
                        f"{context} "
                        f"Payment execution successful."
                    )

                    updated_metadata = {
                        **decision.metadata,
                        "transaction_id":
                            execution_result.transaction_id
                    }

                    # Create NEW immutable-style decision
                    decision = PolicyDecision(
                        status=RefundStatus.COMPLETED,
                        code="REFUND_COMPLETED",
                        reason=(
                            "Refund processed successfully."
                        ),
                        refund_amount=decision.refund_amount,
                        requires_human_review=False,
                        metadata=updated_metadata
                    )

                    # ----------------------------------------------
                    # UPDATE BUSINESS STATE
                    # ----------------------------------------------

                    self.order_repo.update_order_status(
                        order.order_id,
                        order.status
                    )

                    self.customer_repo.update_customer_after_refund(
                        customer_id=customer.customer_id,
                        new_total_spent=(
                            customer.total_spent
                            - decision.refund_amount
                        ),
                        new_refund_count=(
                            customer.refund_count + 1
                        )
                    )

                # ------------------------------------------------------
                # EXECUTION FAILURE
                # ------------------------------------------------------

                else:

                    logger.error(
                        f"{context} "
                        f"Payment execution failed."
                    )

                    decision = PolicyDecision(
                        status=RefundStatus.ESCALATED,
                        code="PAYMENT_EXECUTION_FAILED",
                        reason=(
                            execution_result.execution_message
                        ),
                        refund_amount=decision.refund_amount,
                        requires_human_review=True,
                        metadata={}
                    )

            # ==========================================================
            # 6. FINAL AUDIT RECORD
            # ==========================================================

            logger.info(
                f"{context} Recording final audit trail."
            )

            self.refund_repo.record_final_transaction(
                idempotency_key=idempotency_key,
                order_id=order.order_id,
                decision=decision
            )

            logger.info(
                f"{context} Workflow completed "
                f"with status={decision.status.value}"
            )

            return decision

        except Exception as e:

            logger.exception(
                f"{context} Unexpected workflow crash: {str(e)}"
            )

            return PolicyDecision(
                status=RefundStatus.ESCALATED,
                code="SYSTEM_ERROR",
                reason=(
                    "The system encountered an "
                    "unexpected error."
                ),
                requires_human_review=True,
                metadata={}
            )
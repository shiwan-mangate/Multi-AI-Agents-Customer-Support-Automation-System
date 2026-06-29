import logging

from layer_2_refund.graphs.refund_state import RefundState

from layer_2_refund.schemas.refund_models import (
    RefundStatus,
    PolicyDecision
)

from layer_2_refund.services.mock_payment_service import (
    MockPaymentService
)

logger = logging.getLogger(__name__)

payment_service = MockPaymentService()


def execution_node(state: RefundState):

    decision = state.get("policy_decision")

    order = state.get("order_data")

    workflow_id = state.get(
        "workflow_id"
    )

    id_key = state.get(
        "idempotency_key"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={id_key}"
    )

    if not order or not decision:

        escalated_decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="EXECUTION_PRECONDITION_FAILURE",
            reason=(
                "Execution node triggered "
                "without required workflow context."
            ),
            requires_human_review=True
        )

        failure_log = (
            f"Execution Node | "
            f"Status=CRITICAL_FAILURE | "
            f"{ctx} | "
            f"Code={escalated_decision.code}"
        )

        logger.error(failure_log)

        return {
            "current_node": "execution_node",
            "policy_decision": escalated_decision,
            "error_message": (
                "Execution node missing "
                "required dependencies."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    if decision.status != RefundStatus.APPROVED:

        skip_log = (
            f"Execution Node | "
            f"Status=SKIPPED | "
            f"{ctx} | "
            f"CurrentStatus="
            f"{decision.status.value.upper()}"
        )

        logger.info(skip_log)

        return {
            "current_node": "execution_node",
            "workflow_logs": [
                *state["workflow_logs"],
                skip_log
            ]
        }

    log_header = (
        f"Execution Node | "
        f"Status=STARTING | "
        f"{ctx} | "
        f"Order={order.order_id} | "
        f"Method=MockStripe"
    )

    logger.info(log_header)

    try:

        # ALIGNED: Changed order.amount to order.order_amount
        execution_result = (
            payment_service.execute_refund(
                order_id=order.order_id,
                amount=order.order_amount 
            )
        )

        if execution_result.success:

            completed_decision = (
    decision.model_copy(
        update={
            "status": RefundStatus.COMPLETED,

            "code": "REFUND_EXECUTED",

            "refund_amount": order.order_amount,

            "metadata": {
                **decision.metadata,
                "transaction_id": execution_result.transaction_id,
                "refund_amount": order.order_amount
            }
        }
    )
)

            success_log = (
                f"Execution Node | "
                f"Status=SUCCESS | "
                f"{ctx} | "
                f"TxnID="
                f"{execution_result.transaction_id}"
            )

            logger.info(success_log)

            return {
                "current_node": "execution_node",
                "execution_result": execution_result,
                "policy_decision": completed_decision,
                "review_status": (
                    "COMPLETED"
                    if state.get("review_status")
                    else None
                ),
                "workflow_logs": [
                    *state["workflow_logs"],
                    log_header,
                    success_log
                ]
            }

        escalated_decision = (
            decision.model_copy(
                update={
                    "status":
                        RefundStatus.ESCALATED,

                    "code":
                        "PAYMENT_GATEWAY_FAILURE",

                    "reason": (
                        f"{decision.reason} | "
                        f"Gateway Failure: "
                        f"{execution_result.execution_message}"
                    ),

                    "requires_human_review":
                        True,

                    "metadata": {
                        **decision.metadata,
                        "gateway_error":
                            execution_result.execution_message
                    }
                }
            )
        )

        failure_log = (
            f"Execution Node | "
            f"Status=FAILURE | "
            f"{ctx} | "
            f"Error="
            f"{execution_result.execution_message}"
        )

        logger.warning(failure_log)

        return {
            "current_node": "execution_node",
            "execution_result": execution_result,
            "policy_decision": escalated_decision,
            "workflow_logs": [
                *state["workflow_logs"],
                log_header,
                failure_log
            ]
        }

    except Exception as e:

        logger.exception(
            f"Execution Node | "
            f"Status=UNEXPECTED_EXCEPTION | "
            f"{ctx}"
        )

        escalated_decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="EXECUTION_SYSTEM_FAILURE",
            reason=(
                "Unexpected execution failure "
                "occurred during refund processing."
            ),
            requires_human_review=True
        )

        return {
            "current_node": "execution_node",
            "policy_decision": escalated_decision,
            "error_message": str(e),
            "workflow_logs": [
                *state["workflow_logs"],
                log_header,
                (
                    f"Execution Node | "
                    f"Status=SYSTEM_FAILURE | "
                    f"{ctx}"
                )
            ]
        }
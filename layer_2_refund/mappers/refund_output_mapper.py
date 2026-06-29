from layer_2_refund.schemas.refund_models import (
    RefundOutput
)

from layer_2_refund.builder.response_builder import (
    build_customer_response
)


def build_refund_output(
    final_state: dict
) -> RefundOutput:

    decision = final_state["policy_decision"]

    execution_result = final_state.get(
        "execution_result"
    )

    metrics = final_state.get(
        "metrics"
    )

    request = final_state["request"]

    customer_response = build_customer_response(
        decision=decision,
        order_id=request.order_id,
        execution_result=execution_result
    )

    return RefundOutput(

        ticket_id=request.ticket_id,

        workflow_id=final_state["workflow_id"],

        customer_id=request.customer_id,

        order_id=request.order_id,

        final_status=decision.status,

        decision_code=decision.code,

        decision_reason=decision.reason,

        customer_response=customer_response,

        refund_amount=decision.refund_amount,

        transaction_id=(

            execution_result.transaction_id

            if execution_result

            else None
        ),

        review_required=(
            decision.requires_human_review
        ),

        review_status=final_state.get(
            "review_status"
        ),

        audit_status=final_state.get(
            "audit_status"
        ),

        duration_ms=(

            metrics.duration_ms

            if metrics

            else None
        )
    )
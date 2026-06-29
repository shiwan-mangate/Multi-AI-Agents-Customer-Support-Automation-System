### till now refund agent
import uuid

from langgraph.checkpoint.memory import (
    MemorySaver
)

from layer_2_refund.graphs.refund_graph import (
    refund_graph_builder
)

from layer_2_refund.graphs.state_factory import (
    create_initial_refund_state
)

from layer_2_refund.schemas.refund_models import (
    RefundRequest
)



memory = MemorySaver()


app = refund_graph_builder.compile(

    checkpointer=memory,

    interrupt_before=[
        "human_review_node"
    ]
)



def run_workflow_demo(
    description: str,
    order_id: str
):

    print(
        f"\n{'=' * 70}"
    )

    print(
        f"🚀 SCENARIO: {description}"
    )

    print(
        f"{'=' * 70}"
    )

    thread_id = str(uuid.uuid4())

    config = {

        "configurable": {

            "thread_id": thread_id
        }
    }

    request = RefundRequest(

        ticket_id=f"TKT-{uuid.uuid4().hex[:4]}",

        customer_id="USER-ALPHA",

        order_id=order_id,

        reason_for_refund=(
            "Product damaged during delivery"
        )
    )

    idempotency_key = (triage_output.idempotency_key)

    initial_state = (
        create_initial_refund_state(
            request=request,
            idempotency_key=idempotency_key
        )
    )

    initial_state["workflow_id"] = (
        f"WF-{uuid.uuid4().hex[:6]}"
    )



    print(
        "\n[*] Starting Workflow..."
    )

    for event in app.stream(

        initial_state,

        config,

        stream_mode="values"
    ):

        current_node = event.get(
            "current_node",
            "START"
        )

        decision = event.get(
            "policy_decision"
        )

        if decision:

            print(
                f"    -> Node={current_node} "
                f"| Status={decision.status.value.upper()}"
            )

        else:

            print(
                f"    -> Node={current_node}"
            )

 

    snapshot = app.get_state(config)

    if (

        snapshot.next

        and

        snapshot.next[0]
        == "human_review_node"

    ):

        print(
            "\n⚠️  WORKFLOW INTERRUPTED"
        )

        print(
            "    Awaiting Human Review..."
        )

        decision = snapshot.values.get(
            "policy_decision"
        )

        if decision:

            print(
                f"    Reason={decision.code}"
            )



        print(
            "\n✅ HUMAN ACTION: APPROVE"
        )

        app.update_state(

            config,

            {

                "human_decision": "APPROVE",

                "review_status": "COMPLETED"
            }
        )



        print(
            "\n[*] Resuming Workflow..."
        )

        for _ in app.stream(

            None,

            config,

            stream_mode="values"
        ):

            pass



    final_state = app.get_state(
        config
    ).values

    final_decision = final_state.get(
        "policy_decision"
    )

    print(
        f"\n{'-' * 70}"
    )

    print(
        "📜 FINAL AUDIT LOGS"
    )

    print(
        f"{'-' * 70}"
    )

    for log in final_state.get(
        "workflow_logs",
        []
    ):

        print(
            f"  > {log}"
        )

    print(
        f"\n🏁 FINAL STATUS: "
        f"{final_decision.status.value.upper()}"
    )

    print(
        f"🏁 AUDIT STATUS: "
        f"{final_state.get('audit_status')}"
    )

    metrics = final_state.get("metrics")

    if metrics:

        print(
            f"🏁 DURATION: "
            f"{metrics.duration_ms}ms"
        )

if __name__ == "__main__":

    run_workflow_demo(

        description=(
            "High Value Refund Escalation"
        ),

        order_id="ORD-003"
    )
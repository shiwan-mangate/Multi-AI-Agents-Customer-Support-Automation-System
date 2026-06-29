from langgraph.graph import (
    StateGraph,
    START,
    END
)
from layer_2_refund.graphs.refund_state import (
    RefundState
)

# Nodes
from layer_2_refund.graphs.nodes.idempotency_node import idempotency_node
from layer_2_refund.graphs.nodes.order_node import order_node
from layer_2_refund.graphs.nodes.customer_node import customer_node
from layer_2_refund.graphs.nodes.policy_node import policy_node
from layer_2_refund.graphs.nodes.escalation_node import escalation_node
from layer_2_refund.graphs.nodes.human_review_node import human_review_node
from layer_2_refund.graphs.nodes.execution_node import execution_node
from layer_2_refund.graphs.nodes.audit_node import audit_node

# Routers
from layer_2_refund.graphs.routers import (
    route_after_idempotency,
    route_after_policy,
    route_after_human_review
)


def build_refund_graph(checkpointer):
    """
    Assembles the Layer 2 Refund state machine.
    """
    
    builder = StateGraph(
        RefundState,
        name="refund_orchestration_workflow"
    )

    builder.add_node("idempotency_node", idempotency_node)
    builder.add_node("order_node", order_node)
    builder.add_node("customer_node", customer_node)
    builder.add_node("policy_node", policy_node)
    builder.add_node("escalation_node", escalation_node)
    builder.add_node("human_review_node", human_review_node)
    builder.add_node("execution_node", execution_node)
    builder.add_node("audit_node", audit_node)

    builder.add_edge(START, "idempotency_node")

    builder.add_conditional_edges(
        "idempotency_node",
        route_after_idempotency,
        {
            "order_node": "order_node",
            "audit_node": "audit_node"
        }
    )

    builder.add_edge("order_node", "customer_node")
    builder.add_edge("customer_node", "policy_node")

    builder.add_conditional_edges(
        "policy_node",
        route_after_policy,
        {
            "execution_node": "execution_node",
            "escalation_node": "escalation_node",
            "audit_node": "audit_node"
        }
    )

    builder.add_edge("escalation_node", "human_review_node")

    builder.add_conditional_edges(
        "human_review_node",
        route_after_human_review,
        {
            "human_review_node": "human_review_node",
            "execution_node": "execution_node",
            "audit_node": "audit_node"
        }
    )

    builder.add_edge("execution_node", "audit_node")
    builder.add_edge("audit_node", END)

    # ✅ INJECTED: Compile with the shared Postgres Checkpointer
    refund_graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=[
            "human_review_node"
        ]
    )
    
    return refund_graph
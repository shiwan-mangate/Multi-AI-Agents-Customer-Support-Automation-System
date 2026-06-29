from datetime import datetime, UTC
from typing import Dict, Any
from ..schemas.faq_state import FAQState
import logging

logger = logging.getLogger(__name__)

def retrieval_strategy_node(state: FAQState) -> Dict[str, Any]:
    """
    Adaptive retrieval strategy planner.
    Determines:
    - retrieval mode
    - metadata constraints
    - retry-aware search expansion
    """
    now = datetime.now(UTC)

    intent = state.get("query_intent") or "General FAQ"
    tier = (state.get("customer_tier") or "standard").lower()
    retry_count = state.get("retry_count", 0)

    entities = state.get("entities")
    entities = entities if isinstance(entities, dict) else {}

    strategy = "semantic_search"

    if retry_count > 0:
        strategy = "retry_expanded_search"

    elif entities.get("order_id") or entities.get("product_name"):
        strategy = "context_aware_search"

    intent_mapping = {
    "Refund Policy": "refund_policy",
    "Return Policy": "return_policy",
    "Shipping Policy": "shipping_policy",
    "Account & Billing": "account_&_billing",
    "Subscription Terms": "subscription_terms",
    "Technical Support": "technical_support",
    "Product Warranty": "product_warranty",
    "Privacy & Data": "privacy_&_data",
    "Order Cancellation": "order_cancellation",
    "General FAQ": None,
}

    normalized_category = intent_mapping.get(intent.strip(), None)

    filters: Dict[str, Any] = {}

    if normalized_category:
        filters["category"] = normalized_category

    # FIX: Aligned with strict account_tier schema constraints
    if tier in {"premium", "enterprise"}:
        filters["applicable_tier"] = ["all", "standard", tier]
    else:
        filters["applicable_tier"] = ["all", "standard"]

    logger.warning(
    f"RETRIEVAL STRATEGY | "
    f"intent={intent} | "
    f"normalized_category={normalized_category}"
)

    return {
        "retrieval_strategy": strategy,
        "metadata_filters": filters,
        "current_node": "retrieval_strategy_node",
        "updated_at": now,
        "workflow_logs": [
            {
                "timestamp": now.isoformat(),
                "node": "retrieval_strategy_node",
                "message": f"Retrieval strategy selected: {strategy}",
                "data": {
                    "query_intent": intent,
                    "normalized_category": normalized_category,
                    "strategy": strategy,
                    "filters": filters,
                    "retry_count": retry_count,
                },
            }
        ],
    }
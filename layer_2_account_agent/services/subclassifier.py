import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from layer_2_account_agent.schemas.domain import (
    ActionSubCategory,
    SubclassificationResult
)

logger = logging.getLogger(__name__)


class SubclassifierService:
    """
    Account issue subclassification service.

    Strategy:
    1. deterministic rules first
    2. LLM only for ambiguous cases
    3. clarification as final safe fallback
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.structured_llm = llm.with_structured_output(SubclassificationResult)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are an enterprise customer support classifier.

Classify account issues into ONLY:

- login_issue
- billing_query
- subscription_change
- access_restoration
- security_issue

Rules:
- Security ambiguity defaults to security_issue.
- If intent is unclear, request clarification.
- Return ONLY schema-compliant structured output.
"""
            ),
            ("user", "Customer message: {message}")
        ])

    def classify_issue(self, message: str) -> SubclassificationResult:
        """
        Main classification entrypoint.
        """

        if not message or not message.strip():
            logger.warning("Empty message received for subclassification.")
            return self._trigger_clarification()

        deterministic = self._rule_based_classification(message)
        if deterministic:
            return deterministic

        try:
            chain = self.prompt | self.structured_llm
            return chain.invoke({"message": message})

        except Exception:
            logger.exception("LLM subclassification failed.")
            return self._trigger_clarification()

    # =====================================================
    # RULE ENGINE
    # =====================================================

    def _rule_based_classification(
        self,
        message: str
    ) -> Optional[SubclassificationResult]:
        msg = message.lower()

        security_keywords = [
            "hack",
            "hacked",
            "compromised",
            "unauthorized",
            "fraud",
            "suspicious login",
            "someone logged in",
            "stolen",
            "lost phone",
            "lost 2fa",
            "otp issue",
            "verification code issue"
        ]

        login_keywords = [
            "login",
            "log in",
            "sign in",
            "password",
            "forgot password",
            "locked",
            "account locked"
        ]

        subscription_keywords = [
    "cancel subscription",
    "upgrade subscription",
    "downgrade subscription",
    "pause subscription",
    "billing cycle",
    "plan change",
    "change my plan",
    "cancel my plan",
    "upgrade my plan",
    "downgrade my plan"
]

        billing_keywords = [
        "charge",
        "charged",
        "invoice",
        "receipt",
        "billing",
        "payment",
        "payment failed",
        "payment method",
        "card declined",
        "subscription payment",
        "failed payment",
        "payment issue"
    ]

        access_keywords = [
            "missing feature",
            "premium not working",
            "access missing",
            "paid but no access",
            "feature unavailable",
            "entitlement"
        ]

        if any(k in msg for k in security_keywords):
            return SubclassificationResult(
                sub_category=ActionSubCategory.SECURITY_ISSUE,
                clarification_required=False
            )

        if any(k in msg for k in login_keywords):
            return SubclassificationResult(
                sub_category=ActionSubCategory.LOGIN_ISSUE,
                clarification_required=False
            )

        if any(k in msg for k in subscription_keywords):
            return SubclassificationResult(
                sub_category=ActionSubCategory.SUBSCRIPTION_CHANGE,
                clarification_required=True,
                clarification_question=(
                    "Would you like to upgrade, downgrade, pause, or cancel your subscription?"
                )
            )

        if any(k in msg for k in billing_keywords):
            return SubclassificationResult(
                sub_category=ActionSubCategory.BILLING_QUERY,
                clarification_required=False
            )

        if any(k in msg for k in access_keywords):
            return SubclassificationResult(
                sub_category=ActionSubCategory.ACCESS_RESTORATION,
                clarification_required=False
            )
        return None

    def _trigger_clarification(self) -> SubclassificationResult:
        return SubclassificationResult(
            sub_category=None,
            clarification_required=True,
            clarification_question=(
                "I want to route your account issue correctly. "
                "Are you having login trouble, a billing issue, "
                "a subscription request, or a security concern?"
            )
        )
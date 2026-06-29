import logging

from layer_2_account_agent.schemas.domain import (
    ActionType,
    ActionSubCategory,
    VerificationLevel,
    RiskLevel,
    AccountDecision
)

logger = logging.getLogger(__name__)


class VerificationPolicyService:
    """
    Final authorization gatekeeper.

    Decides whether an account action may proceed based on:
    - verified identity strength
    - unified risk level
    - requested action sensitivity
    """

    SAFE_ACTIONS = {
        ActionType.BILLING_EXPLANATION,
        ActionType.INVOICE_RETRIEVAL
    }

    STANDARD_ACTIONS = {
        ActionType.PASSWORD_RESET,
        ActionType.ACCOUNT_UNLOCK
    }

    SENSITIVE_ACTIONS = {
        ActionType.SUBSCRIPTION_UPGRADE,
        ActionType.SUBSCRIPTION_DOWNGRADE,
        ActionType.SUBSCRIPTION_CANCEL,
        ActionType.SUBSCRIPTION_PAUSE,
        ActionType.PAYMENT_UPDATE_LINK,
        ActionType.ACCESS_SYNC
    }

    VERIFICATION_RANK = {
        VerificationLevel.FAILED: 0,
        VerificationLevel.LOW: 1,
        VerificationLevel.MEDIUM: 2,
        VerificationLevel.HIGH: 3
    }

    REQUIRED_LEVEL = {
        ActionType.BILLING_EXPLANATION: VerificationLevel.LOW,
        ActionType.INVOICE_RETRIEVAL: VerificationLevel.LOW,

        ActionType.PASSWORD_RESET: VerificationLevel.MEDIUM,
        ActionType.ACCOUNT_UNLOCK: VerificationLevel.MEDIUM,

        ActionType.SUBSCRIPTION_UPGRADE: VerificationLevel.HIGH,
        ActionType.SUBSCRIPTION_DOWNGRADE: VerificationLevel.HIGH,
        ActionType.SUBSCRIPTION_CANCEL: VerificationLevel.HIGH,
        ActionType.SUBSCRIPTION_PAUSE: VerificationLevel.HIGH,
        ActionType.PAYMENT_UPDATE_LINK: VerificationLevel.HIGH,
        ActionType.ACCESS_SYNC: VerificationLevel.HIGH
    }

    def evaluate_decision(
        self,
        sub_category: ActionSubCategory,
        requested_action: ActionType,
        verification_level: VerificationLevel,
        risk_level: RiskLevel
    ) -> AccountDecision:
        """
        Final policy decision engine.
        """

        # =====================================================
        # HARD FAILURE: IDENTITY FAILURE
        # =====================================================

        if verification_level == VerificationLevel.FAILED:
            return self._deny(
                sub_category,
                requested_action,
                verification_level,
                risk_level,
                "Identity verification failed.",
                security_escalation=True
            )

        # =====================================================
        # UNKNOWN ACTION SAFETY
        # =====================================================

        required_level = self.REQUIRED_LEVEL.get(requested_action)

        if required_level is None:
            return self._deny(
                sub_category,
                requested_action,
                verification_level,
                risk_level,
                "Unrecognized action type."
            )

        # =====================================================
        # HIGH-RISK SECURITY OVERRIDE
        # =====================================================

        if risk_level == RiskLevel.HIGH:
            if verification_level != VerificationLevel.HIGH:
                return self._deny(
                    sub_category,
                    requested_action,
                    verification_level,
                    risk_level,
                    "High-risk profile requires HIGH verification.",
                    security_escalation=True
                )

            if requested_action in self.SENSITIVE_ACTIONS:
                return self._deny(
                    sub_category,
                    requested_action,
                    verification_level,
                    risk_level,
                    "Sensitive automation blocked for high-risk account.",
                    security_escalation=True
                )

        # =====================================================
        # POLICY MATRIX
        # =====================================================

        current_rank = self.VERIFICATION_RANK[verification_level]
        required_rank = self.VERIFICATION_RANK[required_level]

        if current_rank >= required_rank:
            return self._approve(
                sub_category,
                requested_action,
                verification_level,
                risk_level,
                f"{requested_action.value} approved."
            )

        return self._deny(
            sub_category,
            requested_action,
            verification_level,
            risk_level,
            (
                f"{requested_action.value} requires "
                f"{required_level.value} verification."
            )
        )

    def _approve(
        self,
        sub: ActionSubCategory,
        action: ActionType,
        v_level: VerificationLevel,
        r_level: RiskLevel,
        reason: str
    ) -> AccountDecision:
        logger.info(
            "POLICY APPROVED action=%s verification=%s risk=%s",
            action.value,
            v_level.value,
            r_level.value
        )

        return AccountDecision(
            sub_category=sub,
            requested_action=action,
            verification_level=v_level,
            risk_level=r_level,
            action_allowed=True,
            decision_reason=reason,
            escalation_required=False,
            security_escalation=False
        )

    def _deny(
        self,
        sub: ActionSubCategory,
        action: ActionType,
        v_level: VerificationLevel,
        r_level: RiskLevel,
        reason: str,
        security_escalation: bool = False
    ) -> AccountDecision:
        logger.warning(
            "POLICY DENIED action=%s verification=%s risk=%s reason=%s",
            action.value,
            v_level.value,
            r_level.value,
            reason
        )

        return AccountDecision(
            sub_category=sub,
            requested_action=action,
            verification_level=v_level,
            risk_level=r_level,
            action_allowed=False,
            decision_reason=reason,
            escalation_required=True,
            security_escalation=security_escalation
        )
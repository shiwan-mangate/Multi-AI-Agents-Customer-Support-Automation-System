import logging
import uuid

from layer_2_account_agent.schemas.domain import (
    ProviderResponse,
    ProviderStatus,
    ActionType
)
from layer_2_account_agent.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class BillingProvider:
    """
    Billing / subscription provider adapter.

    Simulates external billing provider behavior
    while persisting state through repository layer.
    """

    PROVIDER_NAME = "InternalBilling"

    SUBSCRIPTION_ACTIONS = {
        ActionType.SUBSCRIPTION_UPGRADE,
        ActionType.SUBSCRIPTION_DOWNGRADE,
        ActionType.SUBSCRIPTION_CANCEL,
        ActionType.SUBSCRIPTION_PAUSE
    }

    STATUS_MAP = {
        ActionType.SUBSCRIPTION_UPGRADE: "active",
        ActionType.SUBSCRIPTION_DOWNGRADE: "active",
        ActionType.SUBSCRIPTION_CANCEL: "cancelled",
        ActionType.SUBSCRIPTION_PAUSE: "paused"
    }

    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def update_subscription(
        self,
        customer_id: int,
        action: ActionType
    ) -> ProviderResponse:
        """
        Execute subscription lifecycle mutation.
        """

        try:
            logger.info(
                "BILLING subscription action customer_id=%s action=%s",
                customer_id,
                action.value
            )

            if action not in self.SUBSCRIPTION_ACTIONS:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.FAILED,
                    error_message=f"Unsupported action: {action.value}"
                )

            subscription = self.account_repo.get_subscription(
                customer_id
            )

            if not subscription:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.FAILED,
                    error_message="No active subscription found."
                )

            target_status = self.STATUS_MAP[action]

            success = self.account_repo.update_subscription_status(
                customer_id=customer_id,
                new_status=target_status
            )

            if success:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.SUCCESS,
                    data={
                        "action": action.value,
                        "customer_id": customer_id,
                        "subscription_id": subscription["subscription_id"],
                        "previous_status": subscription["status"],
                        "new_status": target_status
                    }
                )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.FAILED,
                error_message="Subscription update failed."
            )

        except Exception:
            logger.exception(
                "BILLING subscription mutation failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Billing provider unavailable."
            )

    def generate_payment_link(
        self,
        customer_id: int,
        reason: str = "update_payment_method"
    ) -> ProviderResponse:
        """
        Simulate secure billing portal session generation.
        """

        try:
            logger.info(
                "BILLING payment link customer_id=%s",
                customer_id
            )

            subscription = self.account_repo.get_subscription(
                customer_id
            )

            if not subscription:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.FAILED,
                    error_message="No billing account found."
                )

            session_token = uuid.uuid4().hex[:12]

            secure_link = (
                f"https://billing.example.com/update/"
                f"{customer_id}?session={session_token}"
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.SUCCESS,
                data={
                    "action": "payment_link_generated",
                    "customer_id": customer_id,
                    "reason": reason,
                    "secure_link": secure_link,
                    "expires_in_minutes": 30
                }
            )

        except Exception:
            logger.exception(
                "BILLING payment link generation failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Billing provider unavailable."
            )
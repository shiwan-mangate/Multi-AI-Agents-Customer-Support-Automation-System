import logging

from layer_2_account_agent.schemas.domain import (
    ProviderResponse,
    ProviderStatus
)
from layer_2_account_agent.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class AuthProvider:
    """
    Authentication provider adapter.

    Simulates an external identity provider while delegating
    durable state mutation to AccountRepository.
    """

    PROVIDER_NAME = "InternalIdP"

    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def reset_password(
        self,
        customer_id: int,
        email: str
    ) -> ProviderResponse:
        """
        Trigger password reset workflow.
        """

        try:
            logger.info(
                "AUTH reset password customer_id=%s",
                customer_id
            )

            reset_ok = self.account_repo.update_last_password_reset(
                customer_id
            )

            failed_attempts_reset = (
                self.account_repo.reset_failed_attempts(customer_id)
            )

            if reset_ok:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.SUCCESS,
                    data={
                        "action": "password_reset",
                        "email_sent_to": email,
                        "expires_in_minutes": 15,
                        "failed_attempts_reset": failed_attempts_reset
                    }
                )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.FAILED,
                error_message="Password reset state update failed."
            )

        except Exception:
            logger.exception(
                "AUTH reset password failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Authentication provider unavailable."
            )

    def unlock_account(
        self,
        customer_id: int
    ) -> ProviderResponse:
        """
        Unlock account after successful verification.
        """

        try:
            logger.info(
                "AUTH unlock account customer_id=%s",
                customer_id
            )

            success = self.account_repo.unlock_account(customer_id)

            if success:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.SUCCESS,
                    data={
                        "action": "account_unlocked",
                        "customer_id": customer_id
                    }
                )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.FAILED,
                error_message="Account unlock failed."
            )

        except Exception:
            logger.exception(
                "AUTH unlock failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Authentication provider unavailable."
            )

    def sync_access(
        self,
        customer_id: int
    ) -> ProviderResponse:
        """
        Simulate entitlement refresh / access sync.
        """

        try:
            logger.info(
                "AUTH sync access customer_id=%s",
                customer_id
            )

            auth_record = self.account_repo.get_auth_account(
                customer_id
            )

            if not auth_record:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.FAILED,
                    error_message="No auth account found."
                )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.SUCCESS,
                data={
                    "action": "access_sync_completed",
                    "customer_id": customer_id,
                    "entitlements_refreshed": True
                }
            )

        except Exception:
            logger.exception(
                "AUTH access sync failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Authentication provider unavailable."
            )

    def lock_account(
        self,
        customer_id: int,
        reason: str = "security_flag"
    ) -> ProviderResponse:
        """
        Emergency account lockdown.
        """

        try:
            logger.warning(
                "AUTH lock account customer_id=%s reason=%s",
                customer_id,
                reason
            )

            success = self.account_repo.mark_suspicious(
                customer_id
            )

            if success:
                return ProviderResponse(
                    provider_name=self.PROVIDER_NAME,
                    status=ProviderStatus.SUCCESS,
                    data={
                        "action": "account_locked",
                        "customer_id": customer_id,
                        "reason": reason
                    }
                )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.FAILED,
                error_message="Failed to lock account."
            )

        except Exception:
            logger.exception(
                "AUTH lock failed customer_id=%s",
                customer_id
            )

            return ProviderResponse(
                provider_name=self.PROVIDER_NAME,
                status=ProviderStatus.UNAVAILABLE,
                error_message="Authentication provider unavailable."
            )
import logging
from typing import Dict, Any, Optional

from layer_2_account_agent.schemas.domain import (
    VerificationLevel,
    IdentityResolutionResult
)
from layer_2_account_agent.repositories.customer_repository import CustomerRepository
from layer_2_account_agent.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class IdentityService:
    """
    Zero-trust identity verification service.

    Core question:
    'Do we believe this requester is the legitimate customer?'
    """

    def __init__(
        self,
        customer_repo: CustomerRepository,
        account_repo: AccountRepository
    ):
        self.customer_repo = customer_repo
        self.account_repo = account_repo

    def resolve_identity(
        self,
        email: Optional[str],
        triage_customer_id: Optional[int] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> IdentityResolutionResult:
        """
        Resolve customer identity using layered trust signals.
        """

        signals: Dict[str, Any] = {
            "email_provided": False,
            "customer_exists": False,
            "customer_id_match": False,
            "auth_account_exists": False,
            "suspicious_flag": False,
            "account_locked": False,
            "high_failed_attempts": False,
            "recent_activity_found": False,
            "order_context_match": False
        }

        if not email or not email.strip():
            logger.warning("Identity verification failed: missing email.")
            return self._build_result(
                verified=False,
                confidence=0.0,
                customer_id=None,
                signals=signals
            )

        confidence = 0.0

        try:

            signals["email_provided"] = True

            customer_record = self.customer_repo.get_customer_by_email(email)

            if not customer_record:
                logger.warning(
                    "Identity verification failed: email not found email=%s",
                    email
                )
                return self._build_result(
                    verified=False,
                    confidence=5.0,
                    customer_id=None,
                    signals=signals
                )

            resolved_id = customer_record["customer_id"]
            signals["customer_exists"] = True
            confidence += 45.0

            if triage_customer_id is not None:
                if triage_customer_id == resolved_id:
                    signals["customer_id_match"] = True
                    confidence += 20.0
                else:
                    logger.error(
                        "Identity mismatch triage_customer_id=%s resolved_id=%s",
                        triage_customer_id,
                        resolved_id
                    )

                    return self._build_result(
                        verified=False,
                        confidence=5.0,
                        customer_id=None,
                        signals=signals
                    )


            auth_record = self.account_repo.get_auth_account(resolved_id)

            if auth_record:
                signals["auth_account_exists"] = True
                confidence += 15.0

                if auth_record.get("suspicious_flag"):
                    signals["suspicious_flag"] = True
                   

                if auth_record.get("account_locked"):
                    signals["account_locked"] = True
                    

                failed_attempts = auth_record.get(
                    "failed_login_attempts",
                    0
                )

                if failed_attempts >= 5:
                    signals["high_failed_attempts"] = True
                  

            else:
                confidence -= 10.0


            recent_orders = self.customer_repo.get_recent_orders(
                resolved_id,
                limit=1
            )

            recent_tickets = self.customer_repo.get_ticket_history(
                resolved_id,
                limit=1
            )

            if recent_orders or recent_tickets:
                signals["recent_activity_found"] = True
                confidence += 10.0


            if entities:
                requested_order_id = entities.get("order_id")

                if requested_order_id:
                    for order in recent_orders:
                        if str(order["order_id"]) == str(requested_order_id):
                            signals["order_context_match"] = True
                            confidence += 10.0
                            break

            confidence = max(0.0, min(100.0, confidence))

            verified = confidence >= 60.0

            return self._build_result(
                verified=verified,
                confidence=confidence,
                customer_id=resolved_id,
                signals=signals
            )

        except Exception:
            logger.exception(
                "Identity resolution failed unexpectedly email=%s",
                email
            )

            return self._build_result(
                verified=False,
                confidence=0.0,
                customer_id=None,
                signals=signals
            )

    def _build_result(
        self,
        verified: bool,
        confidence: float,
        customer_id: Optional[int],
        signals: Dict[str, Any]
    ) -> IdentityResolutionResult:
        """
        Map confidence score to verification level.
        """

        if not verified:
            level = VerificationLevel.FAILED
        elif confidence >= 90.0:
            level = VerificationLevel.HIGH
        elif confidence >= 75.0:
            level = VerificationLevel.MEDIUM
        else:
            level = VerificationLevel.LOW

        return IdentityResolutionResult(
            identity_verified=verified,
            identity_confidence=confidence,
            resolved_customer_id=customer_id,
            identity_signals=signals,
            verification_level=level
        )
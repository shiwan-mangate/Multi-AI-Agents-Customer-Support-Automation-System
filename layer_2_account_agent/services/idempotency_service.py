import logging
from typing import Dict, Any, Optional

from layer_2_account_agent.repositories.security_audit_repository import SecurityAuditRepository
from layer_2_account_agent.schemas.domain import ActionType

logger = logging.getLogger(__name__)


class IdempotencyService:
    """
    Business service for idempotent execution control.
    """

    def __init__(
        self,
        security_repo: SecurityAuditRepository
    ):
        self.security_repo = security_repo

    def reserve_execution(
        self,
        idempotency_key: str,
        action_type: ActionType,
        customer_id: Optional[int]
    ) -> bool:
        """
        Reserve execution slot.

        Returns:
            True -> execution allowed
            False -> duplicate or already processing
        """

        try:
            existing = self.security_repo.get_idempotency_record(
                idempotency_key
            )

            if existing:
                status = existing.get("status")

                if status == "completed":
                    logger.info(
                        "Duplicate completed request blocked key=%s",
                        idempotency_key
                    )
                    return False

                if status == "processing":
                    logger.info(
                        "Execution already in progress key=%s",
                        idempotency_key
                    )
                    return False

                if status == "failed":
                    logger.info(
                        "Retrying failed workflow key=%s",
                        idempotency_key
                    )

                    return self.security_repo.update_idempotency_status(
                        idempotency_key=idempotency_key,
                        status="processing",
                        response_payload={}
                    )

            created = self.security_repo.create_idempotency_record(
                idempotency_key=idempotency_key,
                action_type=action_type,
                customer_id=customer_id
            )

            if created:
                logger.info(
                    "Reserved idempotency key=%s",
                    idempotency_key
                )

            return created

        except Exception:
            logger.exception(
                "Failed reserving execution key=%s",
                idempotency_key
            )
            return False

    def get_cached_result(
        self,
        idempotency_key: str
    ) -> Optional[Dict[str, Any]]:
        try:
            existing = self.security_repo.get_idempotency_record(
                idempotency_key
            )

            if not existing:
                return None

            if existing.get("status") != "completed":
                return None

            return existing.get("response_payload")

        except Exception:
            logger.exception(
                "Failed fetching cached result key=%s",
                idempotency_key
            )
            return None

    def mark_completed(
        self,
        idempotency_key: str,
        response_payload: Dict[str, Any]
    ) -> bool:
        return self.security_repo.update_idempotency_status(
            idempotency_key=idempotency_key,
            status="completed",
            response_payload=response_payload
        )

    def mark_failed(
        self,
        idempotency_key: str,
        error_payload: Optional[Dict[str, Any]] = None
    ) -> bool:
        return self.security_repo.update_idempotency_status(
            idempotency_key=idempotency_key,
            status="failed",
            response_payload=error_payload or {}
        )
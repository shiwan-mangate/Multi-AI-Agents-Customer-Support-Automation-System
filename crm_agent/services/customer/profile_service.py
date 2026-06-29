# crm_agent/services/customer/profile_service.py

import logging

from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.repositories.customer_profile_repository import (
    CustomerProfileRepository,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Customer intelligence orchestration layer.

    Business responsibilities:
    - validate customer profile updates
    - enrich profile context
    - delegate persistence

    Persistence responsibilities remain inside:
    CustomerProfileRepository
    """

    def __init__(
        self,
        profile_repo: CustomerProfileRepository,
    ):
        self.profile_repo = profile_repo

    def update_customer_profile(
        self,
        event: CRMResolvedEvent,
    ) -> None:
        """
        Main entry point used by PipelineExecutor.

        Repository owns:
        - atomic UPSERT
        - counter increments
        - frequency tracking
        - concurrency safety

        Service owns:
        - orchestration
        - validation
        - business flow
        """

        customer_id = event.customer.customer_id

        logger.debug(
            "Updating customer profile | customer_id=%s",
            customer_id,
        )

        self._validate_event(event)

        # Delegates execution through the refactored BIGINT repository channel
        self.profile_repo.upsert_profile_from_event(
            event
        )

        logger.info(
            "Customer profile updated | customer_id=%s",
            customer_id,
        )

    def _validate_event(
        self,
        event: CRMResolvedEvent,
    ) -> None:
        """
        Defensive business validation before persistence.
        """

        if not event.customer.customer_id:
            raise ValueError(
                "customer_id is required."
            )

        if not event.event.source_agent:
            raise ValueError(
                "source_agent is required."
            )

        if not event.resolution.status:
            raise ValueError(
                "resolution status is required."
            )

        logger.debug(
            "Profile update validation passed | customer_id=%s",
            event.customer.customer_id,
        )
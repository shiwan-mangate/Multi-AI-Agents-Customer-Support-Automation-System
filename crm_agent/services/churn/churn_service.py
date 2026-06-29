# crm_agent/services/churn/churn_service.py

import logging
from typing import Optional

from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.schemas.churn import ChurnAssessment

from crm_agent.services.churn.churn_engine import ChurnEngine
from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository


logger = logging.getLogger(__name__)


class ChurnService:
    """
    Data-fetching and orchestration layer for churn intelligence.
    
    Responsibilities:
    - Load required state from repositories.
    - Pass state to the deterministic engine.
    - Return the result to the caller (PipelineExecutor).
    
    This service MUST NOT write to the database.
    """

    def __init__(
        self,
        churn_engine: ChurnEngine,
        profile_repo: CustomerProfileRepository,
    ):
        self.churn_engine = churn_engine
        self.profile_repo = profile_repo

    def analyze_customer_risk(
        self,
        event: CRMResolvedEvent,
    ) -> Optional[ChurnAssessment]:
        """
        Gathers context and executes the mathematical churn engine.
        """
        customer_id = event.customer.customer_id
        
        logger.debug(
            "Fetching profile for churn analysis | customer_id=%s", 
            customer_id
        )

        # Strongly typed lookup across the refactored BIGINT interface
        profile = self.profile_repo.get_profile(customer_id)

        if profile is None:
            logger.warning(
                "Cannot calculate churn: Profile missing | customer_id=%s", 
                customer_id
            )
            return None

        logger.debug(
            "Executing churn engine calculations | customer_id=%s", 
            customer_id
        )

        # Business logic handoff remains intact
        assessment = self.churn_engine.calculate_churn_risk(
            profile=profile,
            event=event,
        )

        logger.info(
            "Churn evaluation complete | customer_id=%s | score=%s | level=%s",
            customer_id,
            assessment.churn_score,
            assessment.churn_level,
        )

        return assessment
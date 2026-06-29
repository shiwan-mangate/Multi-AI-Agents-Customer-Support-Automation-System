import logging
from typing import Optional

from sqlalchemy.orm import Session
# Importing the Postgres-specific insert for ON CONFLICT DO UPDATE capability
from sqlalchemy.dialects.postgresql import insert

from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundStatus
)

# Importing the ProcessedRefund model we just created
from layer_2_refund.database.model.process_refund_model import ProcessedRefund

logger = logging.getLogger(__name__)

class RefundRepository:

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    # =====================================================
    # TRUE IDEMPOTENT REPLAY
    # =====================================================

    def get_previous_decision(
        self,
        idempotency_key: str
    ) -> Optional[PolicyDecision]:

        try:
            # Standard ORM lookup matching the idempotency key
            record = self.session.query(ProcessedRefund).filter(
                ProcessedRefund.idempotency_key == idempotency_key
            ).first()

            if not record:
                return None

            return PolicyDecision(
                status=RefundStatus(record.refund_status),
                code="IDEMPOTENT_REPLAY",
                reason=record.decision_reason,
                refund_amount=float(record.refund_amount) if record.refund_amount is not None else None,
                requires_human_review=record.requires_human_review,
                # Using the metadata_ attribute alias defined in the model
                metadata=record.metadata_ or {}
            )

        except Exception:

            self.session.rollback()

            logger.exception(
                "Failed idempotency lookup key=%s",
                idempotency_key
            )

            return None

    # =====================================================
    # FINAL AUDIT STORAGE
    # =====================================================

    def record_final_transaction(
        self,
        idempotency_key: str,
        order_id: int,
        decision: PolicyDecision,
        execution_result=None,
        metadata=None
    ) -> bool:

        try:
            # Build the metadata dictionary (no longer needs json.dumps)
            combined_metadata = {
                **decision.metadata,
                "execution_result": (
                    execution_result.model_dump()
                    if execution_result
                    else None
                ),
                "system_metadata": metadata or {}
            }

            # 1. Build the base insert statement
            # Note: We use `metadata_` here because we are assigning to the Python Model attribute
            stmt = insert(ProcessedRefund).values(
                idempotency_key=idempotency_key,
                order_id=order_id,
                refund_status=decision.status.value,
                decision_reason=decision.reason,
                refund_amount=decision.refund_amount,
                requires_human_review=decision.requires_human_review,
                metadata_=combined_metadata 
            )

            # 2. Append the ON CONFLICT DO UPDATE clause
            stmt = stmt.on_conflict_do_update(
                index_elements=['idempotency_key'],
                set_={
                    'refund_status': stmt.excluded.refund_status,
                    'decision_reason': stmt.excluded.decision_reason,
                    'refund_amount': stmt.excluded.refund_amount,
                    'requires_human_review': stmt.excluded.requires_human_review,
                    
                    # 🔴 THE FIX: Both the Key and the Excluded dictionary must use "metadata" exactly
                    'metadata': stmt.excluded['metadata']
                }
            )

            self.session.execute(stmt)
            self.session.commit()

            return True

        except Exception:

            self.session.rollback()

            logger.exception(
                "Failed recording refund transaction key=%s order_id=%s",
                idempotency_key,
                order_id
            )

            return False
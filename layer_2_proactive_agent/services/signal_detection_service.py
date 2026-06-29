from layer_2_proactive_agent.schemas.signal import Signal
from layer_2_proactive_agent.schemas.signal_assessment import (
    SignalAssessment,
)

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    RiskLevel,
)

from layer_2_proactive_agent.utils.logger import logger


class SignalDetectionService:
    """
    Converts incoming signals into
    business-level assessments.
    """

    def analyze(
        self,
        signal: Signal,
    ) -> SignalAssessment:

        logger.info(
            "Status=START | Operation=SIGNAL_ANALYSIS | "
            "SignalId=%s | SignalType=%s",
            signal.signal_id,
            signal.signal_type.value,
        )

        if signal.signal_type == SignalType.INACTIVE_CUSTOMER:

            assessment = SignalAssessment(
                signal_type=signal.signal_type,
                severity=RiskLevel.MEDIUM,
                detected_reason=(
                    "Customer has been inactive beyond "
                    "configured threshold."
                ),
                requires_immediate_attention=False,
            )

        elif signal.signal_type == SignalType.HIGH_CHURN_RISK:

            assessment = SignalAssessment(
                signal_type=signal.signal_type,
                severity=RiskLevel.HIGH,
                detected_reason=(
                    "Customer churn score exceeded threshold."
                ),
                requires_immediate_attention=True,
            )

        elif (
            signal.signal_type
            == SignalType.RECENT_NEGATIVE_EXPERIENCE
        ):

            assessment = SignalAssessment(
                signal_type=signal.signal_type,
                severity=RiskLevel.HIGH,
                detected_reason=(
                    "Customer recently experienced "
                    "negative support interactions."
                ),
                requires_immediate_attention=True,
            )

        elif (
            signal.signal_type
            == SignalType.VIP_RETENTION_RISK
        ):

            assessment = SignalAssessment(
                signal_type=signal.signal_type,
                severity=RiskLevel.URGENT,
                detected_reason=(
                    "High-value customer exhibits "
                    "retention risk."
                ),
                requires_immediate_attention=True,
            )

        else:
            raise ValueError(
                f"Unsupported signal type: "
                f"{signal.signal_type}"
            )

        logger.info(
            "Status=SUCCESS | "
            "SignalType=%s | Severity=%s",
            assessment.signal_type.value,
            assessment.severity.value,
        )

        return assessment
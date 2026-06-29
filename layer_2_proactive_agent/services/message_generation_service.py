import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from layer_2_proactive_agent.utils.logger import logger
from crm_agent.schemas.customer_profile import CustomerProfile
from layer_2_proactive_agent.schemas.signal_assessment import SignalAssessment
from layer_2_proactive_agent.schemas.risk_assessment import RiskAssessment
from layer_2_proactive_agent.schemas.outreach_message import OutreachMessage
from layer_2_proactive_agent.schemas.enums import SignalType

from layer_2_proactive_agent.prompts.base_prompt import BASE_SYSTEM_PROMPT
from layer_2_proactive_agent.prompts.inactive_customer_prompt import INACTIVE_CUSTOMER_PROMPT
from layer_2_proactive_agent.prompts.high_churn_prompt import CHURN_PROMPT
from layer_2_proactive_agent.prompts.negative_experience_prompt import NEGATIVE_EXPERIENCE_PROMPT
from layer_2_proactive_agent.prompts.vip_retention_prompt import VIP_RETENTION_PROMPT
from langchain_core.language_models.chat_models import BaseChatModel




class MessageGenerationService:
    """
    Generates customer-facing outreach messages 
    from proactive risk signals using a dynamic prompt architecture.
    """
    LANGUAGE_MAP = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "hi": "Hindi",
        "de": "German",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ja": "Japanese",
    }

    def __init__(
        self,
        llm: BaseChatModel
    ):
        self.llm = llm

        self.structured_llm = (
            self.llm.with_structured_output(
                OutreachMessage
            )
        )

    def _get_signal_prompt(self, signal_type: SignalType) -> str:
        """
        Maps the incoming signal type to its specific execution prompt.
        """
        mapping = {
            SignalType.INACTIVE_CUSTOMER: INACTIVE_CUSTOMER_PROMPT,
            SignalType.HIGH_CHURN_RISK: CHURN_PROMPT,
            SignalType.RECENT_NEGATIVE_EXPERIENCE: NEGATIVE_EXPERIENCE_PROMPT,
            SignalType.VIP_RETENTION_RISK: VIP_RETENTION_PROMPT,
        }
        if signal_type not in mapping:
            raise ValueError(f"No prompt configured for signal type: {signal_type}")
            
        logger.info(
            "Status=PROMPT_SELECTED | SignalType=%s",
            signal_type.value,
        )
        return mapping[signal_type]

    def _build_customer_context(
        self,
        customer_profile: CustomerProfile,
        risk_assessment: RiskAssessment,
        signal_assessment: SignalAssessment,
    ) -> str:
        """
        Formats the CRM and intelligence payloads into a clean 
        context string for the LLM human message.
        """
        raw_lang = getattr(customer_profile, "preferred_language", "en")
        language = self.LANGUAGE_MAP.get(raw_lang, "English")
        
        churn_level = getattr(customer_profile.churn_intelligence, "churn_level", "UNKNOWN")

        context = f"""
        Customer Information:
        - Tier: {customer_profile.tier}
        - LTV: {customer_profile.ltv}
        - Churn Level: {churn_level}

        Signal Information:
        - Signal Type: {signal_assessment.signal_type.value}
        - Severity: {signal_assessment.severity.value}
        - Reason: {signal_assessment.detected_reason}

        Risk Information:
        - Risk Level: {risk_assessment.risk_level.value}
        - Risk Score: {risk_assessment.risk_score}

        Output Language:
        - Generate the final outreach message strictly in {language}.
        """
        logger.info(
            "Status=CONTEXT_BUILT | Customer=%s | Language=%s",
            customer_profile.customer_id,
            language
        )
        return context

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _invoke_llm(self, system_prompt: str, human_prompt: str) -> OutreachMessage:
        """
        Isolated LLM invocation method strictly scoping the retry and network logic.
        """
        return self.structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )

    def generate(
        self,
        customer_profile: CustomerProfile,
        risk_assessment: RiskAssessment,
        signal_assessment: SignalAssessment,
    ) -> OutreachMessage:
        """
        Produces a customer-facing outreach message based on dynamic context.
        """
        logger.info(
            "Status=START | "
            "Operation=MESSAGE_GENERATION | "
            "Customer=%s",
            customer_profile.customer_id,
        )

        try:
            signal_prompt = self._get_signal_prompt(signal_assessment.signal_type)
            system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{signal_prompt}"
            human_prompt = self._build_customer_context(
                customer_profile=customer_profile,
                risk_assessment=risk_assessment,
                signal_assessment=signal_assessment
            )
            message = self._invoke_llm(system_prompt, human_prompt)
            if not message.subject.strip():
                raise ValueError("Generated message missing subject.")
            if not message.body.strip():
                raise ValueError("Generated message missing body.")
            message = message.model_copy(
                update={
                    "generated_by": MODEL_NAME
                }
            )
            logger.info(
                "Status=SUCCESS | "
                "Operation=MESSAGE_GENERATION | "
                "Customer=%s",
                customer_profile.customer_id,
            )
            return message
        except Exception as exc:
            logger.exception(
                "Status=FAILED | "
                "Operation=MESSAGE_GENERATION | "
                "Customer=%s | Error=%s",
                customer_profile.customer_id,
                str(exc),
            )
            return OutreachMessage(
                subject="Checking In",
                body=(
                    "Hello,\n\n"
                    "We wanted to check in and make sure "
                    "everything is going well. "
                    "Please let us know if we can assist."
                ),
                channel="email",
                generated_by="fallback_template",
            )
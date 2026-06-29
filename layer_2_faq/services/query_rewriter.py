from typing import Optional, Dict, Any

from pydantic import ValidationError
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from ..schemas.faq_models import QueryUnderstandingOutput
from ..prompts.rewrite_prompt import QUERY_REWRITE_PROMPT


class QueryRewriterService:
    """
    Stateless domain service responsible for transforming
    raw customer messages into structured, search-optimized
    queries using a Reasoning LLM.
    """

    def __init__(
        self,
        llm: BaseChatModel
    ):
        self.llm = llm

        self.structured_llm = (
            self.llm.with_structured_output(
                QueryUnderstandingOutput
            )
        )

        self.prompt_template = (
            PromptTemplate.from_template(
                QUERY_REWRITE_PROMPT
            )
        )

    def rewrite_query(
        self,
        message_raw: str,
        entities: Dict[str, Any],
        order_context: Optional[Dict[str, Any]],
        customer_tier: str,
        retry_count: int,
        correction_note: Optional[str]
    ) -> QueryUnderstandingOutput:
        """
        Executes the LLM transformation pipeline.

        Returns:
            QueryUnderstandingOutput

        Raises:
            RuntimeError
        """

        safe_order_context = (
            str(order_context)
            if order_context
            else "None"
        )

        safe_entities = (
            str(entities)
            if entities
            else "None"
        )

        safe_correction = (
            correction_note
            if correction_note
            else "None"
        )

        try:

            formatted_prompt = (
                self.prompt_template.format(
                    message_raw=message_raw,
                    entities=safe_entities,
                    order_context=safe_order_context,
                    customer_tier=customer_tier,
                    retry_count=retry_count,
                    correction_note=safe_correction
                )
            )

            response: QueryUnderstandingOutput = (
                self.structured_llm.invoke(
                    formatted_prompt
                )
            )

            return response

        except ValidationError as e:

            raise RuntimeError(
                "Query rewriting failed. "
                f"LLM violated output schema: {str(e)}"
            )

        except Exception as e:

            raise RuntimeError(
                "Query rewriting failed during "
                f"LLM invocation: {str(e)}"
            )
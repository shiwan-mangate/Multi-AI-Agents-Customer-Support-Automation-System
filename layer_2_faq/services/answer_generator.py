import logging
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser 

from ..schemas.faq_models import AnswerGenerationOutput

logger = logging.getLogger(__name__)


class AnswerGeneratorService:
    """
    Grounded answer synthesis service.
    """

    MAX_CONTEXT_CHARS = 2000

    def __init__(
        self,
        llm: BaseChatModel
    ):
        self.llm = llm

       
        self.parser = PydanticOutputParser(pydantic_object=AnswerGenerationOutput)

       
        self.prompt = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
You are a highly constrained enterprise FAQ AI.

RULES:
1. Use ONLY provided KNOWLEDGE BASE CONTEXT.
2. Never use external knowledge.
3. Never invent policies, procedures, or exceptions.
4. If answer exists:
   - knowledge_gap=False
   - grounded_answer must be complete
   - citations required
5. If answer does NOT exist:
   - knowledge_gap=True
   - grounded_answer MUST be ""
   - citations MUST be []
6. CRM context may personalize tone only.
   It must NEVER alter policy facts.

{format_instructions}
"""
                    ),
                    (
                        "user",
                        """
CUSTOMER QUERY:
{query}

CRM CONTEXT:
{crm_context}

KNOWLEDGE BASE CONTEXT:
{kb_context}
"""
                    )
                ]
            ).partial(format_instructions=self.parser.get_format_instructions())
        )

        # 🟢 FIX: Chain the prompt, LLM, and parser together
        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    def generate(
        self,
        query: str,
        parent_contexts: List[Dict[str, Any]],
        crm_data: Dict[str, Any]
    ) -> AnswerGenerationOutput:

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if not parent_contexts:
            return AnswerGenerationOutput(
                knowledge_gap=True,
                grounded_answer="",
                citations=[]
            )

        kb_text = "\n".join(
            [
                (
                    f"[Doc: {d.get('document_name', 'Unknown')} "
                    f"| Section: {d.get('section', 'General')}]\n"
                    f"{d.get('full_answer', '')[:self.MAX_CONTEXT_CHARS]}"
                )
                for d in parent_contexts
            ]
        )

        crm_text = (
            "\n".join(
                [
                    f"{k}: {v}"
                    for k, v in crm_data.items()
                    if v is not None
                ]
            )
            or "No CRM data."
        )

        try:
            # 🟢 FIX: Invoke the new chain
            result = self.chain.invoke(
                {
                    "query": query,
                    "crm_context": crm_text,
                    "kb_context": kb_text
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Answer generation failed: {str(e)}"
            )

            raise RuntimeError(
                f"Answer generator failure: {str(e)}"
            )
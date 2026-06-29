import os
import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from ..schemas.faq_models import VerificationOutput
logger = logging.getLogger(__name__)


class VerifyAnswerService:
    """
    Critic layer for grounded QA verification.
    """
    MAX_CONTEXT_CHARS = 2000
    def __init__(self,model_name: str = "llama-3.1-8b-instant"):
        groq_api_key = os.environ.get("GROQ_API_KEY")

        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required."
            )

        self.llm = ChatGroq(
            model=model_name,
            temperature=0.0,
            api_key=groq_api_key,
            timeout=30
        )

        self.structured_evaluator = (
            self.llm.with_structured_output(
                VerificationOutput
            )
        )

        self.prompt = (
            ChatPromptTemplate.from_messages([
                ("system",
                    """
You are an enterprise QA verifier.

Evaluate:
1. Faithfulness
2. Relevance
3. Citation integrity

Scoring:
1.0 = perfect
0.7 = acceptable
0.3 = weak
0.0 = hallucinated/failure

If score < 0.7:
verdict MUST be fail.
"""),
("user",
"""
QUERY:
{query}

KB CONTEXT:
{kb_context}

ANSWER:
{grounded_answer}

CITATIONS:
{citations}
""")
])
)

        self.chain = (
            self.prompt
            | self.structured_evaluator
        )

    def verify(
        self,
        query: str,
        grounded_answer: str,
        citations: List[Dict[str, Any]],
        parent_contexts: List[Dict[str, Any]]
    ) -> VerificationOutput:

        
        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not parent_contexts:
            raise ValueError(
                "Parent contexts required."
            )

        if not grounded_answer:
            return VerificationOutput(
                verifier_score=1.0,
                verdict="pass",
                failure_reason=None
            )

        kb_text = "\n".join([
            (
                f"[Doc: {d.get('document_name')} "
                f"| Section: {d.get('section')}]\n"
                f"{d.get('full_answer', '')[:self.MAX_CONTEXT_CHARS]}"
            )
            for d in parent_contexts
        ])

        citations_text = "\n".join([
            (
                f"- {c.get('document_name')} "
                f"({c.get('section')}): "
                f"'{c.get('relevance_quote')}'"
            )
            for c in citations
        ]) or "No citations provided."

        try:
            result = self.chain.invoke({
                "query": query,
                "kb_context": kb_text,
                "grounded_answer": grounded_answer,
                "citations": citations_text
            })

            return result

        except Exception as e:
            logger.error(
                f"Verifier failed: {str(e)}"
            )

            raise RuntimeError(
                f"Verifier service failure: {str(e)}"
            )
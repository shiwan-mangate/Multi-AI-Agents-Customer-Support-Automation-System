from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, UTC

class FAQBaseModel(BaseModel):
    """Base configuration for all FAQ domain models."""
    model_config = ConfigDict(populate_by_name=True)

class RetrievedChunk(FAQBaseModel):
    """Represents a specific unit of knowledge retrieved from the vector database."""
    chunk_id: str = Field(..., description="Unique identifier for the child chunk")
    parent_id: str = Field(..., description="Identifier for the source document")
    content: str = Field(..., description="The actual text content of the chunk")
    similarity_score: Optional[float] = Field(None, description="Vector similarity score")
    rerank_score: Optional[float] = Field(None, description="Relevance score from reranker")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Citation(FAQBaseModel):
    """Traceability mapping for UI rendering and audits."""
    document_name: str = Field(..., description="Exact name of the source document used.")
    section: str = Field(..., description="Section of the document.")
    source_type: Literal["pdf", "markdown", "html", "web", "knowledge_base"] = Field(default="knowledge_base")
    relevance_quote: str = Field(..., description="A short, exact quote from the document that justifies this part of the answer.")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class AnswerGenerationOutput(FAQBaseModel):
    """Strict output schema for the generation node."""
    knowledge_gap: bool = Field(
        ..., 
        description="Set to True ONLY if the provided context DOES NOT contain the answer. If True, leave grounded_answer blank."
    )
    grounded_answer: str = Field(
        ..., 
        description="The customer-facing response. Must be polite, professional, and directly answer the query using ONLY the provided context."
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="List of exact sources used to formulate the grounded_answer."
    )
class AttemptRecord(FAQBaseModel):
    """Trace of a single reasoning/retrieval attempt for debugging and loops."""
    attempt_number: int
    rewritten_query: Optional[str] = None
    retrieval_strategy: Optional[str] = None
    retrieved_chunk_ids: List[str] = Field(default_factory=list)
    verifier_score: Optional[float] = None
    failure_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class ClarificationRequest(FAQBaseModel):
    """Data required to pause the graph and ask the user for more info."""
    question: str = Field(...)
    reason: str = Field(..., description="Logic for why clarification is needed")
    required_entity: Optional[str] = Field(None, description="The specific missing entity")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class KnowledgeGapRecord(FAQBaseModel):
    """Logged when the RAG system fails to find relevant documentation."""
    query: str = Field(...)
    reason: str = Field(...)
    severity: Literal["low", "medium", "high"] = Field(default="medium")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class QueryUnderstandingOutput(BaseModel):
    """Structured output contract for the Query Rewriter Service."""
    rewritten_query: str = Field(..., description="The optimized semantic search string")
    query_intent: str = Field(..., description="The categorized intent (e.g., Refund Policy)")
    is_ambiguous: bool = Field(..., description="True if the query lacks necessary context to answer")

class VerificationOutput(FAQBaseModel):
    """
    Strict output schema for the Critic/Verifier node.
    Evaluates faithfulness, relevance, and citation integrity.
    """
    verifier_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="""
        Score rubric:
        1.0 = Fully faithful, relevant, and well-cited.
        0.7 = Mostly correct, but slightly weak relevance or citation.
        0.3 = Partially unsupported by the KB context.
        0.0 = Hallucinated, factually wrong, or completely irrelevant.
        """
    )
    verdict: Literal["pass", "fail"] = Field(
        ...,
        description="If the verifier_score is < 0.7, this MUST be 'fail'."
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="If verdict is 'fail', provide a highly specific explanation of what was hallucinated, irrelevant, or poorly cited."
    )
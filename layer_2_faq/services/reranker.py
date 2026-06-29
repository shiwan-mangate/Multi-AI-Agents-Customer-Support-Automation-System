import logging
from typing import List, Dict, Any

from flashrank import Ranker, RerankRequest

logger = logging.getLogger(__name__)


class RerankerService:
    """
    Runtime semantic reranking service using FlashRank.
    """
    def __init__(self,model_name: str = "ms-marco-MiniLM-L-12-v2"):
        logger.info(f"Initializing FlashRank model: {model_name}")

        self.ranker = Ranker(model_name=model_name)

        logger.info("Reranker ready.")

    def rerank_candidates(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be > 0"
            )

        if not chunks:
            return []

        passages = []

        for chunk in chunks:
            if not chunk.get("chunk_id"):
                continue

            if not chunk.get("content"):
                continue

            passages.append({
                "id": chunk["chunk_id"],
                "text": chunk["content"],
                "meta": chunk
            })

        if not passages:
            return []

        try:
            rerank_request = RerankRequest(
                query=query,
                passages=passages
            )

            results = self.ranker.rerank(
                rerank_request
            )
            for result in results[:3]:
                logger.warning(
                    f"RERANK DEBUG | "
                    f"id={result['id']} | "
                    f"score={result['score']}"
                )

        except Exception as e:
            logger.error(
                f"FlashRank failure: {str(e)}"
            )

            raise RuntimeError(
                f"Reranker failure: {str(e)}"
            )

        reranked_chunks = []

        for result in results[:top_k]:
            original_chunk = result["meta"]

            enriched = original_chunk.copy()
            enriched["rerank_score"] = float(
                result["score"]
            )

            reranked_chunks.append(enriched)

        return reranked_chunks
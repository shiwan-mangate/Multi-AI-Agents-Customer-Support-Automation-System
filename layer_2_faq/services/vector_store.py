import os
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, text
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Runtime FAQ semantic retrieval service.
    """

    EXPECTED_DIMENSION = 384

    def __init__(
        self,
        db_url: Optional[str] = None,
        model_name: str = "BAAI/bge-small-en-v1.5"
    ):
        self.db_url = db_url or os.environ.get(
            "FAQ_DATABASE_URL"
        )

        if not self.db_url:
            raise ValueError(
                "FAQ_DATABASE_URL environment variable required."
            )

        self.engine = create_engine(
            self.db_url,
            pool_pre_ping=True
        )

        self.embedding_model = TextEmbedding(
            model_name=model_name
        )

    def embed_query(
        self,
        query: str
    ) -> List[float]:
        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        try:
            vector = list(
                self.embedding_model.embed([query])
            )[0].tolist()

            if len(vector) != self.EXPECTED_DIMENSION:
                raise ValueError(
                    "Embedding dimension mismatch."
                )

            return vector

        except Exception as e:
            raise RuntimeError(
                f"Query embedding failed: {str(e)}"
            )

    def search_candidates(
        self,
        query: str,
        filters: Dict[str, Any],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        query_vector = self.embed_query(query)

        vector_literal = (
            "[" + ",".join(map(str, query_vector)) + "]"
        )

        category = filters.get("category")
        logger.warning(f"FILTERS RECEIVED = {filters}")
        logger.warning(f"CATEGORY RECEIVED = {category}")
        applicable_tiers = filters.get(
            "applicable_tier",
            ["all"]
        )

        if category:
            category = category.lower().replace(" ", "_")
            logger.warning(f"NORMALIZED CATEGORY = {category}")

        tier_literal = (
            "ARRAY[" +
            ",".join(
                f"'{tier}'"
                for tier in applicable_tiers
            ) +
            "]::TEXT[]"
        )

        sql = f"""
            SELECT
                c.chunk_id,
                c.parent_id,
                c.content,
                c.category,
                p.document_name,
                p.section,
                GREATEST(
                    0,
                    1 - (
                        c.embedding <=> CAST(:vector AS VECTOR)
                    )
                ) AS similarity_score
            FROM faq_child_chunks c
            JOIN faq_parent_documents p
                ON c.parent_id = p.parent_id
            WHERE c.applicable_tier && {tier_literal}
        """

        params = {
            "vector": vector_literal,
            "top_k": top_k,
        }

        logger.warning(f"SQL PARAMS = {params}")
        logger.warning(f"SQL QUERY = {sql}")

        if category:
            sql += " AND c.category = :category"
            params["category"] = category

        sql += """
            ORDER BY c.embedding
                <=> CAST(:vector AS VECTOR)
            LIMIT :top_k
        """

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(
                    text(sql),
                    params
                ).mappings().all()

                return [
                    {
                        "chunk_id": row["chunk_id"],
                        "parent_id": row["parent_id"],
                        "content": row["content"],
                        "document_name": row["document_name"],
                        "section": row["section"],
                        "category": row["category"],
                        "similarity_score": float(
                            row["similarity_score"]
                        ),
                    }
                    for row in rows
                ]

        except Exception as e:
            raise RuntimeError(
                f"Vector search failed: {str(e)}"
            )

    def get_parent_context(
        self,
        parent_ids: List[str]
    ) -> List[Dict[str, Any]]:
        if not parent_ids:
            return []

        unique_ids = list(set(parent_ids))

        sql = text("""
            SELECT
                parent_id,
                faq_id,
                question,
                full_answer,
                category,
                document_name,
                section
            FROM faq_parent_documents
            WHERE parent_id = ANY(:parent_ids)
        """)

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(
                    sql,
                    {"parent_ids": unique_ids}
                ).mappings().all()

                return [
                    dict(row)
                    for row in rows
                ]

        except Exception as e:
            raise RuntimeError(
                f"Parent context fetch failed: {str(e)}"
            )
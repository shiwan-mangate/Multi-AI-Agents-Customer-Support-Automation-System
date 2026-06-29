import json
import logging
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class FAQVectorRepository:
    """
    PostgreSQL + pgvector persistence layer
    for FAQ parent documents and child embeddings.
    """

    def __init__(self, db_url: str):
        self.engine: Engine = create_engine(
            db_url,
            pool_pre_ping=True
        )

    def save_faq_record(
        self,
        parent_record: Dict[str, Any],
        child_chunks: List[Dict[str, Any]]
    ) -> None:
        parent_id = parent_record["parent_id"]
        faq_id = parent_record["faq_id"]

        delete_sql = text("""
            DELETE FROM faq_parent_documents
            WHERE parent_id = :parent_id
        """)

        insert_parent_sql = text("""
            INSERT INTO faq_parent_documents
            (
                parent_id,
                faq_id,
                question,
                full_answer,
                category,
                document_name,
                section,
                metadata
            )
            VALUES
            (
                :parent_id,
                :faq_id,
                :question,
                :full_answer,
                :category,
                :document_name,
                :section,
                :metadata
            )
        """)

        insert_child_sql = text("""
            INSERT INTO faq_child_chunks
            (
                chunk_id,
                parent_id,
                content,
                embedding,
                category,
                applicable_tier,
                tags
            )
            VALUES
            (
                :chunk_id,
                :parent_id,
                :content,
                :embedding,
                :category,
                CAST(:applicable_tier AS TEXT[]),
                :tags
            )
        """)

        parent_payload = {
            "parent_id": parent_id,
            "faq_id": faq_id,
            "question": parent_record["question"],
            "full_answer": parent_record["answer"],
            "category": parent_record["category"],
            "document_name": parent_record["document_name"],
            "section": parent_record.get("section"),
            "metadata": json.dumps(
                parent_record.get("metadata", {})
            ),
        }

        children_payload = []

        for child in child_chunks:
            if not child.get("embedding"):
                continue

            vector_literal = (
                "[" + ",".join(map(str, child["embedding"])) + "]"
            )

            children_payload.append({
                "chunk_id": child["chunk_id"],
                "parent_id": child["parent_id"],
                "content": child["content"],
                "embedding": vector_literal,
                "category": child["category"],
                "applicable_tier": child["applicable_tier"],
                "tags": json.dumps(child.get("tags", [])),
            })

        try:
            with self.engine.begin() as conn:
                conn.execute(delete_sql, {
                    "parent_id": parent_id
                })

                conn.execute(insert_parent_sql, parent_payload)

                if children_payload:
                    conn.execute(
                        insert_child_sql,
                        children_payload
                    )

            logger.info(
                f"Saved FAQ {parent_id} with "
                f"{len(children_payload)} child chunks."
            )

        except Exception as e:
            logger.error(
                f"Database transaction failed for "
                f"{parent_id}: {str(e)}"
            )
            raise RuntimeError(
                f"Failed to persist FAQ record: {str(e)}"
            )

    def get_document_count(self) -> int:
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) "
                    "FROM faq_parent_documents"
                )
            )
            return result.scalar_one()
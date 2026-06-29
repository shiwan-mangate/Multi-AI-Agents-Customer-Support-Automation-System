import os
import logging
from collections import defaultdict
from typing import Optional, Dict, List, Any

from .faq_parser import FAQParser
from .faq_chunker import FAQChunker
from .embedder import FAQEmbedder
from .pgvector_repository import FAQVectorRepository

logger = logging.getLogger(__name__)


class FAQIngestionPipeline:
    """
    Offline ETL pipeline for FAQ vector database ingestion.
    """

    def __init__(
        self,
        db_url: Optional[str] = None
    ):
        self.db_url = db_url or os.environ.get(
            "FAQ_DATABASE_URL"
        )

        if not self.db_url:
            raise ValueError(
                "FAQ_DATABASE_URL environment variable is required."
            )

        logger.info("Initializing ingestion pipeline...")

        self.parser = FAQParser()
        self.chunker = FAQChunker()
        self.embedder = FAQEmbedder()
        self.repository = FAQVectorRepository(self.db_url)

        logger.info("Pipeline initialized successfully.")

    def run(
        self,
        markdown_file_path: str,
        document_name: str
    ) -> None:
        logger.info(
            f"Starting ingestion for {markdown_file_path}"
        )

        if not os.path.exists(markdown_file_path):
            raise FileNotFoundError(
                f"File not found: {markdown_file_path}"
            )

        with open(
            markdown_file_path,
            "r",
            encoding="utf-8"
        ) as file:
            markdown_text = file.read()

        parent_records = self.parser.parse_document(
            markdown_text,
            document_name
        )

        if not parent_records:
            raise RuntimeError(
                "No FAQ records extracted from document."
            )

        logger.info(
            f"Parsed {len(parent_records)} parent records."
        )

        child_chunks = self.chunker.create_chunks(
            parent_records
        )

        if not child_chunks:
            raise RuntimeError(
                "No child chunks generated."
            )

        logger.info(
            f"Generated {len(child_chunks)} child chunks."
        )

        embedded_chunks = self.embedder.embed_chunks(
            child_chunks
        )

        if not embedded_chunks:
            raise RuntimeError(
                "Embedding generation failed."
            )

        logger.info(
            f"Generated embeddings for "
            f"{len(embedded_chunks)} chunks."
        )

        grouped_chunks = defaultdict(list)

        for chunk in embedded_chunks:
            grouped_chunks[
                chunk["parent_id"]
            ].append(chunk)

        for parent in parent_records:
            self.repository.save_faq_record(
                parent,
                grouped_chunks.get(
                    parent["parent_id"],
                    []
                )
            )

        total_docs = self.repository.get_document_count()

        logger.info(
            f"Ingestion complete. "
            f"Total parent docs in DB: {total_docs}"
        )
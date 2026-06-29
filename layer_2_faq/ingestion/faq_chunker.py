from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FAQChunker:
    """
    Converts parent FAQ records into child chunks for semantic retrieval.
    Implements Parent-Child RAG chunking.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

    def create_chunks(
        self,
        parent_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        all_child_chunks: List[Dict[str, Any]] = []

        for parent in parent_records:
            parent_id = parent.get("parent_id")
            full_text = parent.get("answer")

            if not parent_id or not full_text:
                continue

            chunks = self.splitter.split_text(full_text)

            for i, chunk_content in enumerate(chunks, start=1):
                content = chunk_content.strip()

                if not content:
                    continue

                child_record = {
                    "chunk_id": f"{parent_id}_chunk_{i}",
                    "parent_id": parent_id,
                    "content": content,
                    "category": parent.get("category"),
                    "applicable_tier": self._extract_tiers(
                        parent.get("metadata", {})
                    ),
                    "tags": parent.get("tags", []),
                    "document_name": parent.get("document_name"),
                    "section": parent.get("section"),
                }

                all_child_chunks.append(child_record)

        return all_child_chunks

    def _extract_tiers(
        self,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Converts tier metadata into normalized TEXT[] format.
        """
        tier_str = str(metadata.get("tier", "all")).lower()

        tiers = [t.strip() for t in tier_str.split(",") if t.strip()]

        if "all" in tiers or not tiers:
            return ["all"]

        return tiers
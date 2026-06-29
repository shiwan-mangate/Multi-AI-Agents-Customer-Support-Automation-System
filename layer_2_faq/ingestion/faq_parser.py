import re
from typing import List, Dict, Any, Optional


class FAQParser:
    """
    Parses structured FAQ markdown knowledge-base documents
    into standardized ingestion-ready records.
    """

    def parse_document(
        self,
        markdown_text: str,
        document_name: str
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        current_section: Optional[str] = None
        current_question: Optional[str] = None
        current_answer_lines: List[str] = []

        metadata: Dict[str, Any] = {}
        category = "general_faq"
        qa_counter = 1

        lines = markdown_text.splitlines()

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            # Metadata
            meta_match = re.match(
                r'^\*\*(Category|Version|Last Updated|Tier):\*\*\s*(.+)$',
                stripped,
                re.IGNORECASE
            )
            if meta_match:
                key = meta_match.group(1).lower().replace(" ", "_")
                value = meta_match.group(2).strip()

                metadata[key] = value

                if key == "category":
                    category = value.lower().replace(" ", "_")

                continue

            # Section
            sec_match = re.match(r'^##\s+(.*)', stripped)
            if sec_match:
                if current_question:
                    record = self._build_record(
                        document_name,
                        qa_counter,
                        current_question,
                        current_answer_lines,
                        category,
                        current_section,
                        metadata
                    )
                    if record:
                        results.append(record)
                        qa_counter += 1

                current_question = None
                current_answer_lines = []
                current_section = sec_match.group(1).strip()
                continue

            # Question
            q_match = re.match(r'^\*\*Q:\s*(.*?)\*\*$', stripped)
            if q_match:
                if current_question:
                    record = self._build_record(
                        document_name,
                        qa_counter,
                        current_question,
                        current_answer_lines,
                        category,
                        current_section,
                        metadata
                    )
                    if record:
                        results.append(record)
                        qa_counter += 1

                current_question = q_match.group(1).strip()
                current_answer_lines = []
                continue

            # Answer body
            if current_question:
                if stripped.startswith("A:"):
                    current_answer_lines.append(stripped[2:].strip())
                else:
                    current_answer_lines.append(stripped)

        # Final flush
        if current_question:
            record = self._build_record(
                document_name,
                qa_counter,
                current_question,
                current_answer_lines,
                category,
                current_section,
                metadata
            )
            if record:
                results.append(record)

        return results

    def _build_record(
        self,
        doc_name: str,
        index: int,
        question: str,
        answer_lines: List[str],
        category: str,
        section: Optional[str],
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Constructs final FAQ record.
        Skips malformed empty answers.
        """
        full_answer = "\n".join(answer_lines).strip()

        if not full_answer:
            return None
        
        record_id = f"{doc_name}_qa_{index}"

        return {
            "parent_id": record_id,
            "faq_id": record_id,
            "question": question,
            "answer": full_answer,
            "category": category,
            "document_name": doc_name,
            "section": section,
            "metadata": metadata.copy(),
        }
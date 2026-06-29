# layer_4_analytics/reports/knowledge_gap_report_service.py
from typing import List
from layer_4_analytics.schemas.knowledge_gap import KnowledgeGap

class KnowledgeGapReportService:
    """
    Presentation layer for Knowledge Base Intelligence.
    Consumes validated KnowledgeGap schemas and transforms them into 
    human-readable, formatted text reports for Content and Success teams.
    Contains zero business logic or calculations.
    """

    @staticmethod
    def generate_report(gaps: List[KnowledgeGap]) -> str:
        """
        Generates a structured, prioritized Knowledge Gap text report.
        Groups by severity and sorts by occurrences for maximum readability.
        """
       
        if not gaps:
            return (
                "==================================================\n"
                "KNOWLEDGE GAP REPORT\n"
                "==================================================\n\n"
                "No significant knowledge gaps were detected\n"
                "during the reporting period.\n\n"
                "Customer support interactions appear to be\n"
                "adequately covered by current documentation.\n\n"
                "=================================================="
            )

       
        sorted_gaps = sorted(gaps, key=lambda x: x.occurrences, reverse=True)

        
        grouped_gaps = {
    "HIGH": [g for g in sorted_gaps if str(g.severity).lower() == "high"],
    "MEDIUM": [g for g in sorted_gaps if str(g.severity).lower() == "medium"],
    "LOW": [g for g in sorted_gaps if str(g.severity).lower() == "low"]
}

        
        parts = [
            "==================================================",
            "KNOWLEDGE GAP REPORT",
            "==================================================",
            f"\nTotal Knowledge Gaps Identified: {len(gaps)}\n"
        ]

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            severity_gaps = grouped_gaps[severity]
            if not severity_gaps:
                continue

            parts.append("--------------------------------------------------")
            parts.append(f"{severity} PRIORITY GAPS")
            parts.append("--------------------------------------------------")

            for gap in severity_gaps:
                display_topic = gap.topic.replace("_", " ").title()

                parts.append("")
                parts.append("Topic:")
                parts.append(display_topic)
                parts.append("")
                
                parts.append("Occurrences:")
                parts.append(str(gap.occurrences))
                parts.append("")
                
                parts.append("Customer Satisfaction:")
                parts.append(f"{gap.satisfaction_rate:,.2f}%")
                parts.append("")
                
                parts.append("Suggested Article:")
                parts.append(gap.suggested_article_title)
                parts.append("")
                
                parts.append("Recommended Action:")
                parts.append(gap.suggested_action)
                parts.append("")
                
                parts.append("Example Questions:\n")
                
               
                if gap.sample_questions:
                    for question in gap.sample_questions:
                        parts.append(f"• {question}")
                else:
                    parts.append("• No example questions available")
                
                parts.append("")
                parts.append("--------------------------------------------------")

        if parts[-1] == "--------------------------------------------------":
            parts.pop()

        parts.append("")
        parts.append("==================================================")
        parts.append("END OF REPORT")
        parts.append("==================================================")

        return "\n".join(parts)
# layer_4_analytics/services/knowledge_gap_service.py

from typing import List, Dict, Any
from layer_4_analytics.schemas.knowledge_gap import KnowledgeGap


class KnowledgeGapService:
    """
    Intelligent business logic engine that transforms raw customer complaints 
    into actionable content-creation workflows for the Customer Success team.
    """


    HIGH_SEVERITY_MIN = 40
    MEDIUM_SEVERITY_MIN = 15

   
    SUGGESTED_TITLES = {
        "faq": "General Frequently Asked Questions",
        "refund_request": "Understanding Refund Processing",
        "account_issue": "Managing Your Account Settings",
        "technical_bug": "Troubleshooting Known Technical Issues",
        "angry_complex": "Escalation & Advanced Support Guide"
    }

    @staticmethod
    def calculate_knowledge_gaps(mapped_feedback_rows: List[Dict[str, Any]]) -> List[KnowledgeGap]:
        """
        Groups raw feedback questions by topic, calculates domain satisfaction,
        and generates specific KnowledgeGap action items compliant with GapActionType.
        """

        topic_data: Dict[str, Dict[str, Any]] = {}

        for row in mapped_feedback_rows:
            topic = row.get("topic", "unknown_topic")
            
            if topic not in topic_data:
                topic_data[topic] = {
                    "occurrences": 0,
                    "positive_feedback": 0,
                    "questions": set()  
                }

            topic_data[topic]["occurrences"] += 1
            
            if row.get("feedback_type") == "positive":
                topic_data[topic]["positive_feedback"] += 1

            question_text = row.get("question")
            if question_text:
                topic_data[topic]["questions"].add(question_text)

        results: List[KnowledgeGap] = []

   
        for topic, data in topic_data.items():
            occurrences = data["occurrences"]
            
            satisfaction_rate = 0.0
            if occurrences > 0:
                satisfaction_rate = (data["positive_feedback"] / occurrences) * 100.0

         
            if occurrences >= KnowledgeGapService.HIGH_SEVERITY_MIN:
                severity = "high"
                suggested_action = "CREATE_FAQ_ARTICLE"
            elif occurrences >= KnowledgeGapService.MEDIUM_SEVERITY_MIN:
                severity = "medium"
                suggested_action = "UPDATE_EXISTING_ARTICLE"
            else:
                severity = "low"
               
                suggested_action = "UPDATE_EXISTING_ARTICLE"

        
            article_title = KnowledgeGapService.SUGGESTED_TITLES.get(
                topic, 
                f"Guide to {topic.replace('_', ' ').title()}" 
            )

       
            gap = KnowledgeGap(
                cluster_id=f"kg_{topic}",
                topic=topic,
                occurrences=occurrences,
                severity=severity,
                satisfaction_rate=round(satisfaction_rate, 2),
                sample_questions=list(data["questions"])[:5],
                suggested_article_title=article_title,
                suggested_action=suggested_action
            )
            
            results.append(gap)

        return sorted(results, key=lambda x: x.occurrences, reverse=True)
    
    
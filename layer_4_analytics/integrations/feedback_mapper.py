# layer_4_analytics/integrations/feedback_mapper.py
from typing import Dict, List, Any


class FeedbackMapper:
    """
    Anti-Corruption Layer (ACL) for Customer Feedback and Knowledge Context.
    Translates raw database rows into clean, stable analytical inputs for both 
    the SatisfactionAnalyticsService and the KnowledgeGapService.
    """
    
  
    UNKNOWN_FEEDBACK = "unknown"
    UNKNOWN_TOPIC = "unknown_topic"

    @staticmethod
    def map_feedback_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a single raw feedback database dictionary into a clean analytics dictionary.
        Normalizes string casing, strips whitespace, and safely handles NULL values.
        """
        raw_feedback = row.get("feedback")
        raw_topic = row.get("topic")
        raw_question = row.get("question")

        if raw_feedback is not None:
            feedback_val = str(raw_feedback).lower().strip()
            is_positive = feedback_val in ["positive", "good", "yes", "👍", "1"]
            is_negative = feedback_val in ["negative", "bad", "no", "👎", "0"]
            feedback_type = "positive" if is_positive else ("negative" if is_negative else "neutral")
        else:
            feedback_type = FeedbackMapper.UNKNOWN_FEEDBACK

       
        if raw_topic is not None:
            normalized_topic = str(raw_topic).lower().strip()
        else:
            normalized_topic = FeedbackMapper.UNKNOWN_TOPIC


        if raw_question is not None:
            cleaned_question = str(raw_question).strip()
        else:
            cleaned_question = ""

        return {
            "feedback_type": feedback_type,
            "topic": normalized_topic,
            "question": cleaned_question
        }

    @classmethod
    def map_feedback_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.map_feedback_row(row) for row in rows]
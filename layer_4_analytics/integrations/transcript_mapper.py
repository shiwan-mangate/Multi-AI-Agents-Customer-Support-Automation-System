# layer_4_analytics/integrations/transcript_mapper.py

from typing import Dict, List, Any


class TranscriptMapper:
    """
    Anti-Corruption Layer (ACL) for Ticket Transcripts.
    Normalizes string casings, handles missing resolution times, and strictly prepares 
    clean inputs for the Agent, Intent, ROI, and Satisfaction Analytics Services.
    """


    
    @staticmethod
    def map_agent_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares raw transcript data for the AgentPerformanceService.
        Converts milliseconds to seconds preserving float precision, and normalizes status strings.
        """
        raw_agent = row.get("agent_name")
        raw_status = row.get("status")
        raw_time_ms = row.get("time_to_resolution_ms")

        return {
            "agent_name": str(raw_agent).lower().strip() if raw_agent else "unknown_agent",
            "status": str(raw_status).lower().strip() if raw_status else "unknown",
            "resolution_time_seconds": (float(raw_time_ms) / 1000.0) if raw_time_ms is not None else 0.0
        }

    @classmethod
    def map_agent_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.map_agent_row(row) for row in rows]



    @staticmethod
    def map_intent_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares raw transcript data for the IntentAnalyticsService.
        Renames the DB column `intent` to the schema-compliant `intent_name`.
        """
        raw_intent = row.get("intent")

        return {
            "intent_name": str(raw_intent).lower().strip() if raw_intent else "unclassified"
        }

    @classmethod
    def map_intent_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.map_intent_row(row) for row in rows]



    @staticmethod
    def map_roi_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares raw transcript data for the ROIAnalyticsService.
        Handles multi-tenant tracking and normalizes resolution categorizations.
        """
        raw_id = row.get("customer_id")
        raw_name = row.get("customer_name")
        raw_res_type = row.get("resolution_type")
        raw_status = row.get("status")

        return {
           
            "customer_id": raw_id,
            "customer_name": str(raw_name).strip() if raw_name else "Unknown Customer",
            
          
            "resolution_type": str(raw_res_type).lower().strip() if raw_res_type else "unknown",
            "status": str(raw_status).lower().strip() if raw_status else "unknown"
        }

    @classmethod
    def map_roi_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.map_roi_row(row) for row in rows]



    @staticmethod
    def map_feedback_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares raw transcript data for SatisfactionAnalyticsService and KnowledgeGapService.
        Normalizes feedback flags (e.g., 'positive', '👍') into standard boolean/string states.
        """
        raw_feedback = row.get("feedback")
        raw_topic = row.get("topic")
        raw_question = row.get("question")

       
        feedback_val = str(raw_feedback).lower().strip() if raw_feedback else "neutral"
        is_positive = feedback_val in ["positive", "good", "yes", "👍", "1"]
        is_negative = feedback_val in ["negative", "bad", "no", "👎", "0"]
        
        normalized_feedback = "positive" if is_positive else ("negative" if is_negative else "neutral")

        return {
            "feedback_type": normalized_feedback,
            "topic": str(raw_topic).strip() if raw_topic else "Unknown Topic",
            "question_text": str(raw_question).strip() if raw_question else ""
        }

    @classmethod
    def map_feedback_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.map_feedback_row(row) for row in rows]
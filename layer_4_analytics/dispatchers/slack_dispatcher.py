# layer_4_analytics/dispatchers/slack_dispatcher.py

import logging
import requests
from layer_4_analytics.config.settings import settings

logger = logging.getLogger(__name__)

class SlackDispatcher:
    """
    Infrastructure Adapter for Slack Delivery.
    Strictly consumes pre-formatted strings and handles webhook transmission.
    Contains absolutely zero analytics, formatting, or database logic.
    """

    def __init__(self):
   
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self._is_configured = bool(self.webhook_url)
        
      
        if not self._is_configured:
            logger.warning("Slack webhook URL is not configured. Dispatches will be skipped.")

    def _send_message(self, message: str) -> bool:
        """
        Internal helper to handle the actual HTTP POST request to the webhook.
        """
        if not self._is_configured:
            return False

       
        payload = {
            "text": message
        }

        try:

            response = requests.post(
                self.webhook_url, 
                json=payload, 
                timeout=10
            )
            
           
            response.raise_for_status()
            
            logger.info("Successfully dispatched message to Slack")
            return True

        except requests.exceptions.Timeout:
            logger.exception("Slack webhook request timed out after 10 seconds")
            return False
            
        except requests.exceptions.RequestException:
          
            logger.exception("Failed to dispatch message to Slack")
            return False



    def send_churn_alert(self, report_text: str) -> bool:
        formatted_message = f"🚨 *HIGH RISK CUSTOMER DETECTED*\n\n{report_text}"
        return self._send_message(formatted_message)

    def send_knowledge_gap_summary(self, report_text: str) -> bool:
        formatted_message = f"📚 *KNOWLEDGE GAP ALERT*\n\n{report_text}"
        return self._send_message(formatted_message)

    def send_executive_summary(self, report_text: str) -> bool:
        formatted_message = f"📊 *EXECUTIVE SUMMARY REPORT*\n\n{report_text}"
        return self._send_message(formatted_message)
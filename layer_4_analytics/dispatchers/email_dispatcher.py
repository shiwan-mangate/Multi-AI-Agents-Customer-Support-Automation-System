# layer_4_analytics/dispatchers/email_dispatcher.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Union, List
import logging
from layer_4_analytics.config.settings import settings

logger = logging.getLogger(__name__)

class EmailDispatcher:
    """
    Infrastructure Adapter for Email Delivery.
    Strictly consumes pre-formatted strings and handles network transmission.
    Contains absolutely zero analytics, formatting, or database logic.
    """

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SMTP_SENDER
        self.sender_password = settings.SMTP_PASSWORD

    def _send_email(self, recipient: Union[str, List[str]], subject: str, body: str) -> bool:
        """
        Internal helper to handle the actual SMTP connection, strict MIME headers, 
        and multi-recipient envelope routing.
        """
        
        recipients = recipient if isinstance(recipient, list) else [recipient]
        header_to = ", ".join(recipients)

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = header_to
        msg['Subject'] = subject

        
        msg.attach(MIMEText(body, 'plain'))

        try:
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()  
                
                if self.sender_password:
                    server.login(self.sender_email, self.sender_password)
                
                
                server.send_message(
                    msg, 
                    from_addr=self.sender_email, 
                    to_addrs=recipients
                )
                
            logger.info(f"Successfully dispatched '{subject}' to {header_to}")
            return True

        except Exception:
          
            logger.exception(f"Failed to dispatch email '{subject}' to {header_to}")
            return False

    # ==========================================
    # PUBLIC DISPATCH METHODS
    # ==========================================

    def send_roi_report(self, recipient: Union[str, List[str]], report_text: str) -> bool:
        subject = "Monthly ROI Performance Report"
        return self._send_email(recipient, subject, report_text)

    def send_knowledge_gap_report(self, recipient: Union[str, List[str]], report_text: str) -> bool:
        subject = "Weekly Knowledge Gap Analysis"
        return self._send_email(recipient, subject, report_text)

    def send_executive_summary(self, recipient: Union[str, List[str]], report_text: str) -> bool:
        subject = "Executive Summary Report"
        return self._send_email(recipient, subject, report_text)
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

# Import the core Ticket model from the Triage Agent to prevent schema duplication
from layer_2_triage.database.model.ticket_model import Ticket

logger = logging.getLogger(__name__)

NOISE_NODES = {
    "state_factory",
    "validate_contract_node",
    "audit_node",
    "notification_dispatch_node",
}

class ConversationRepository:
    """
    Repository for conversational evidence reconstruction.

    Responsibilities:
    - transcript reconstruction
    - workflow action extraction
    - historical ticket retrieval

    No business logic.
    """

    def __init__(self, session: Session):
        self.session = session

    def build_conversation_transcript(
        self,
        ticket_id: str,
        current_message: str,
        workflow_logs: List[Dict[str, Any]]
    ) -> str:
        """
        Build flattened transcript for escalation brief generation.
        """

        transcript_lines = []

        if current_message:
            transcript_lines.append(
                f"Customer [Ticket {ticket_id}]: {current_message}"
            )

        sorted_logs = sorted(
            workflow_logs,
            key=lambda log: log.get("timestamp", "")
        )

        for log in sorted_logs:
            timestamp = log.get("timestamp", "")
            node = log.get("node", "system")
            message = log.get("message", "Executed action.")

            time_prefix = f"[{timestamp}] " if timestamp else ""

            if node.startswith("system") or node == "state_factory":
                transcript_lines.append(
                    f"System: {time_prefix}{message}"
                )
            else:
                transcript_lines.append(
                    f"Agent ({node}): {time_prefix}{message}"
                )

        return "\n".join(transcript_lines)

    def extract_agent_actions(
        self,
        workflow_logs: List[Dict[str, Any]],
        source_agent: str
    ) -> List[Dict[str, Any]]:
        """
        Convert workflow logs into structured agent actions.
        """

        actions = []

        sorted_logs = sorted(
            workflow_logs,
            key=lambda log: log.get("timestamp", "")
        )

        for log in sorted_logs:
            node = log.get("node", "unknown_node")

            if node in NOISE_NODES:
                continue

            message = log.get("message", "")
            data = log.get("data", {})

            actions.append({
                "agent_name": source_agent,
                "action": node,
                "result": message,
                "metadata": data
            })

        return actions

    def get_recent_ticket_history(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent ticket history.
        """
        try:
            results = self.session.query(
                Ticket.ticket_id,
                Ticket.issue_type,
                Ticket.sentiment,
                Ticket.priority,
                Ticket.resolved,
                Ticket.created_at
            ).filter(
                Ticket.customer_id == customer_id
            ).order_by(
                Ticket.created_at.desc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching ticket history customer_id=%s",
                customer_id
            )
            return []
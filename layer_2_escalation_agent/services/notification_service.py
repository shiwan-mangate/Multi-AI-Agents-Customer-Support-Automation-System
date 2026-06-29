import html
import logging
from typing import Dict, Any, List, Set

from layer_2_escalation_agent.schemas.human_brief import HumanBrief
from layer_2_escalation_agent.schemas.customer_context import CustomerContext
from layer_2_escalation_agent.schemas.trigger_assessment import TriggerAssessment
from layer_2_escalation_agent.schemas.risk_assessment import RiskAssessment
from layer_2_escalation_agent.schemas.routing_decision import RoutingDecision
from layer_2_escalation_agent.schemas.notification_job import NotificationJob, NotificationChannel

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Deterministic Notification Fanout + Payload Orchestration Service.
    """

    MAX_SLACK_TEXT = 2000
    MAX_EMAIL_TEXT = 5000
    MAX_PAGER_TEXT = 300

    TEAM_RECIPIENTS = {
        "security_incident_response": {
            "dashboard": "queue_security",
            "slack": "#incidents-security",
            "email": "security-escalations@company.com",
            "pager": "oncall-security",
        },
        "legal_response_team": {
            "dashboard": "queue_legal",
            "slack": "#incidents-legal",
            "email": "legal-escalations@company.com",
            "pager": "oncall-legal",
        },
        "retention_team": {
            "dashboard": "queue_retention",
            "slack": "#alerts-churn",
            "email": "vip-retention@company.com",
        },
        "billing_operations_team": {
            "dashboard": "queue_billing",
            "slack": "#alerts-billing",
            "email": "billing-ops@company.com",
        },
        "support_specialist_team": {
            "dashboard": "queue_specialist",
            "slack": "#alerts-specialist",
        },
        "customer_resolution_team": {
            "dashboard": "queue_resolution",
            "slack": "#alerts-resolution",
        },
        "technical_incident_team": {
            "dashboard": "queue_tech_ops",
            "slack": "#incidents-tech",
            "email": "tech-ops@company.com",
            "pager": "oncall-tech",
        },
        "general_support_team": {
            "dashboard": "queue_general",
            "slack": "#alerts-general",
            "email": "support-t2@company.com",
        },
    }

    def build_jobs(
        self,
        case_id: str,
        ticket_id: str,  # Refactored: ticket_id typed as string primitive to align with DB character varying
        human_brief: HumanBrief,
        routing_decision: RoutingDecision,
        risk_assessment: RiskAssessment,
        customer_context: CustomerContext,
        trigger_assessment: TriggerAssessment,
    ) -> List[NotificationJob]:
        """
        Build durable outbox-ready notification jobs.
        """
        # Refactored: Coerce to standard string token to prevent serialization mismatches
        risk_level = risk_assessment.level.value.lower() if hasattr(risk_assessment.level, "value") else str(risk_assessment.level).lower()
        category = trigger_assessment.category.value.lower() if hasattr(trigger_assessment.category, "value") else str(trigger_assessment.category).lower()
        
        assigned_team = routing_decision.assigned_team
        customer_tier = str(customer_context.customer_tier).lower()

        channels = self._select_channels(
            risk_level=risk_level,
            category=category,
            risk_assessment=risk_assessment,
            customer_tier=customer_tier,
        )

        jobs: List[NotificationJob] = []

        for channel in channels:
            recipient = self._resolve_recipient(
                team=assigned_team,
                channel=channel.value,
            )

            if channel == NotificationChannel.DASHBOARD:
                payload = self._build_dashboard_payload(
                    case_id,
                    ticket_id,
                    assigned_team,
                    human_brief,
                    risk_level,
                )

            elif channel == NotificationChannel.SLACK:
                payload = self._build_slack_payload(
                    case_id,
                    assigned_team,
                    human_brief,
                    risk_level,
                )

            elif channel == NotificationChannel.EMAIL:
                payload = self._build_email_payload(
                    case_id,
                    ticket_id,
                    human_brief,
                    risk_level,
                )

            elif channel == NotificationChannel.PAGER:
                payload = self._build_pager_payload(
                    case_id,
                    category,
                    risk_level,
                )

            else:
                logger.warning(
                    "Skipping unsupported notification channel=%s",
                    channel,
                )
                continue

            jobs.append(
                NotificationJob(
                    case_id=case_id,
                    channel=channel,
                    recipient=recipient,
                    payload=payload,
                )
            )

        logger.info(
            "Notification jobs created | case=%s | team=%s | channels=%s | total=%d",
            case_id,
            assigned_team,
            [c.value for c in channels],
            len(jobs),
        )

        return jobs

    def _select_channels(
        self,
        risk_level: str,
        category: str,
        risk_assessment: RiskAssessment,
        customer_tier: str,
        ) -> List[NotificationChannel]:
            channels: Set[NotificationChannel] = {
                NotificationChannel.DASHBOARD
            }

            if risk_level in {"high", "urgent"}:
                channels.add(NotificationChannel.SLACK)

            if (
                risk_level == "urgent"
                or category == "legal"
                or risk_assessment.security_risk
                or customer_tier == "enterprise"
            ):
                channels.add(NotificationChannel.EMAIL)

            if (
                risk_level == "urgent"
                and category in {"security", "legal", "operational"}
            ):
                channels.add(NotificationChannel.PAGER)

            return list(channels)

    def _resolve_recipient(
        self,
        team: str,
        channel: str,
    ) -> str:
        """
        Resolve delivery endpoint.
        """
        normalized_team = (team or "general_support_team").strip().lower()
        team_mapping = self.TEAM_RECIPIENTS.get(normalized_team)

        if not team_mapping:
            logger.warning(
                "Missing team mapping for %s. Falling back to general support.",
                normalized_team,
            )
            team_mapping = self.TEAM_RECIPIENTS["general_support_team"]

        recipient = team_mapping.get(channel)

        if not recipient:
            logger.warning(
                "Missing channel mapping | team=%s | channel=%s",
                normalized_team,
                channel,
            )
            recipient = "unknown-recipient"

        return recipient

    def _truncate(
        self,
        text: str,
        max_len: int,
    ) -> str:
        if not text:
            return ""

        if len(text) <= max_len:
            return text

        return text[:max_len] + "..."

    def _build_dashboard_payload(
        self,
        case_id: str,
        ticket_id: str,  # Refactored: Type signature aligned
        assigned_team: str,
        brief: HumanBrief,
        risk_level: str,
    ) -> Dict[str, Any]:
        return {
            "case_id": case_id,
            "ticket_id": ticket_id,
            "assigned_team": assigned_team,
            "priority": risk_level.upper(),
            "brief": brief.model_dump(),
        }

    def _build_slack_payload(
        self,
        case_id: str,
        assigned_team: str,
        brief: HumanBrief,
        risk_level: str,
    ) -> Dict[str, Any]:
        icon = "🚨" if risk_level.lower() in {"high", "critical"} else "⚠️"

        markdown_text = (
            f"{icon} *{risk_level.upper()} ESCALATION: {case_id}*\n"
            f"*Team:* {assigned_team}\n"
            f"*Customer:* {brief.customer_summary}\n"
            f"*Issue:* {brief.issue_summary}\n"
            f"*Blockers:* {', '.join(brief.blockers)}\n"
            f"*Action:* {brief.recommended_next_action}\n"
            f"_{brief.urgency_reason}_"
        )

        markdown_text = self._truncate(markdown_text, self.MAX_SLACK_TEXT)

        return {
            "text": markdown_text,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": markdown_text,
                    },
                }
            ],
        }

    def _build_email_payload(
        self,
        case_id: str,
        ticket_id: str,  # Refactored: Type signature aligned
        brief: HumanBrief,
        risk_level: str,
    ) -> Dict[str, Any]:
        safe_customer = html.escape(brief.customer_summary)
        safe_issue = html.escape(brief.issue_summary)
        safe_action = html.escape(brief.recommended_next_action)

        safe_actions = "".join(
            f"<li>{html.escape(action)}</li>"
            for action in brief.attempted_actions
        )

        subject = self._truncate(
            f"[{risk_level.upper()}] Escalation {case_id}",
            250,
        )

        body_html = f"""
        <h2>Escalation Case: {html.escape(case_id)}</h2>
        <p><strong>Ticket Reference:</strong> {html.escape(ticket_id)}</p>
        <p><strong>Customer:</strong> {safe_customer}</p>
        <p><strong>Issue Summary:</strong> {safe_issue}</p>
        <ul>{safe_actions}</ul>
        <p><strong>Recommended Action:</strong> {safe_action}</p>
        """

        body_text = self._truncate(
            f"Escalation {case_id}\nIssue: {brief.issue_summary}",
            self.MAX_EMAIL_TEXT,
        )

        return {
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
        }

    def _build_pager_payload(
        self,
        case_id: str,
        category: str,
        risk_level: str,
    ) -> Dict[str, Any]:
        message = (
            f"{risk_level.upper()} {category.upper()} ESCALATION | "
            f"CASE {case_id} | Immediate action required."
        )

        return {
            "alert_message": self._truncate(
                message,
                self.MAX_PAGER_TEXT,
            )
        }
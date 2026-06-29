"""create crm tables

Revision ID: 5bfb7b38709d
Revises:
Create Date: 2026-05-26 10:52:08.935291
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "5bfb7b38709d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "churn_alerts",
        sa.Column("alert_id", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.String(length=64), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("tier", sa.String(length=50), nullable=False),
        sa.Column("ltv", sa.Numeric(12, 2), nullable=False),
        sa.Column("source_agent", sa.String(length=50), nullable=True),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("risk_reasons", postgresql.ARRAY(sa.String(length=255)), nullable=False),
        sa.Column("alert_status", sa.String(length=20), nullable=False),
        sa.Column("delivery_status", sa.String(length=20), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False),
        sa.Column("acknowledged_by", sa.String(length=100), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("alert_id"),
    )

    op.create_index("idx_alert_delivery", "churn_alerts", ["delivery_status", "created_at"])
    op.create_index("idx_alert_ops_dashboard", "churn_alerts", ["alert_status", "severity"])
    op.create_index("idx_alert_suppression", "churn_alerts", ["customer_id", "alert_status", "created_at"])

    op.create_table(
        "crm_events",
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("source_agent", sa.String(length=50), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("claimed_by", sa.String(length=100), nullable=True),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_index("idx_crm_queue_polling", "crm_events", ["status", "created_at"])
    op.create_index("ix_crm_events_created_at", "crm_events", ["created_at"])
    op.create_index("ix_crm_events_event_type", "crm_events", ["event_type"])
    op.create_index("ix_crm_events_source_agent", "crm_events", ["source_agent"])
    op.create_index("ix_crm_events_status", "crm_events", ["status"])

    op.create_table(
        "customer_support_profiles",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("tier", sa.String(length=50), nullable=False),
        sa.Column("ltv", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_tickets", sa.Integer(), nullable=False),
        sa.Column("total_faq_tickets", sa.Integer(), nullable=False),
        sa.Column("total_refund_tickets", sa.Integer(), nullable=False),
        sa.Column("total_account_tickets", sa.Integer(), nullable=False),
        sa.Column("total_escalations", sa.Integer(), nullable=False),
        sa.Column("total_denials", sa.Integer(), nullable=False),
        sa.Column("total_failures", sa.Integer(), nullable=False),
        sa.Column("total_clarifications", sa.Integer(), nullable=False),
        sa.Column("total_duplicate_suppressions", sa.Integer(), nullable=False),
        sa.Column("repeat_negative_count", sa.Integer(), nullable=False),
        sa.Column("repeat_escalation_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_request_count", sa.Integer(), nullable=False),
        sa.Column("negative_ticket_count", sa.Integer(), nullable=False),
        sa.Column("last_sentiment", sa.String(length=50), nullable=True),
        sa.Column("sentiment_history", postgresql.ARRAY(sa.String(length=50)), nullable=False),
        sa.Column("churn_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("churn_level", sa.String(length=50), nullable=False),
        sa.Column("churn_last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issue_frequency", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("agent_interaction_frequency", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("languages_used", postgresql.ARRAY(sa.String(length=10)), nullable=False),
        sa.Column("preferred_language", sa.String(length=10), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_ticket_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("customer_id"),
    )

    op.create_index("idx_customer_churn", "customer_support_profiles", ["churn_level"])
    op.create_index("idx_customer_last_ticket", "customer_support_profiles", ["last_ticket_at"])
    op.create_index("ix_customer_support_profiles_customer_email", "customer_support_profiles", ["customer_email"])

    op.create_table(
        "feedback_signals",
        sa.Column("feedback_id", sa.String(length=64), nullable=False),
        sa.Column("ticket_id", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("source_agent", sa.String(length=50), nullable=False),
        sa.Column("feedback_type", sa.String(length=50), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("feedback_channel", sa.String(length=50), nullable=True),
        sa.Column("resolution_type", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("processed_for_churn", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("feedback_id"),
    )

    op.create_index("idx_feedback_agent", "feedback_signals", ["source_agent", "rating", "created_at"])
    op.create_index("idx_feedback_customer", "feedback_signals", ["customer_id", "created_at"])
    op.create_index("idx_feedback_ticket", "feedback_signals", ["ticket_id"], unique=True)

    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result_status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_table(
        "ticket_transcripts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("source_agent", sa.String(length=50), nullable=False),
        sa.Column("workflow_id", sa.String(length=100), nullable=True),
        sa.Column("trace_id", sa.String(length=100), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=True),
        sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("agents_involved", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("original_message", sa.Text(), nullable=True),
        sa.Column("translated_message", sa.Text(), nullable=True),
        sa.Column("intent", sa.String(length=100), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("sentiment_start", sa.String(length=20), nullable=True),
        sa.Column("sentiment_end", sa.String(length=20), nullable=True),
        sa.Column("issue_tags", postgresql.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("resolution_type", sa.String(length=100), nullable=False),
        sa.Column("resolution_message", sa.Text(), nullable=True),
        sa.Column("resolved_by", sa.String(length=50), nullable=False),
        sa.Column("time_to_resolution_ms", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_transcript_agent_perf", "ticket_transcripts", ["resolved_by", "created_at"])
    op.create_index("idx_transcript_analytics", "ticket_transcripts", ["intent", "created_at"])
    op.create_index("idx_transcript_customer", "ticket_transcripts", ["customer_id", "created_at"])
    op.create_index("ix_ticket_transcripts_created_at", "ticket_transcripts", ["created_at"])
    op.create_index("ix_ticket_transcripts_source_agent", "ticket_transcripts", ["source_agent"])
    op.create_index("ix_ticket_transcripts_status", "ticket_transcripts", ["status"])
    op.create_index("ix_ticket_transcripts_ticket_id", "ticket_transcripts", ["ticket_id"])


def downgrade() -> None:
    op.drop_index("ix_ticket_transcripts_ticket_id", table_name="ticket_transcripts")
    op.drop_index("ix_ticket_transcripts_status", table_name="ticket_transcripts")
    op.drop_index("ix_ticket_transcripts_source_agent", table_name="ticket_transcripts")
    op.drop_index("ix_ticket_transcripts_created_at", table_name="ticket_transcripts")
    op.drop_index("idx_transcript_customer", table_name="ticket_transcripts")
    op.drop_index("idx_transcript_analytics", table_name="ticket_transcripts")
    op.drop_index("idx_transcript_agent_perf", table_name="ticket_transcripts")
    op.drop_table("ticket_transcripts")

    op.drop_table("processed_events")

    op.drop_index("idx_feedback_ticket", table_name="feedback_signals")
    op.drop_index("idx_feedback_customer", table_name="feedback_signals")
    op.drop_index("idx_feedback_agent", table_name="feedback_signals")
    op.drop_table("feedback_signals")

    op.drop_index("ix_customer_support_profiles_customer_email", table_name="customer_support_profiles")
    op.drop_index("idx_customer_last_ticket", table_name="customer_support_profiles")
    op.drop_index("idx_customer_churn", table_name="customer_support_profiles")
    op.drop_table("customer_support_profiles")

    op.drop_index("ix_crm_events_status", table_name="crm_events")
    op.drop_index("ix_crm_events_source_agent", table_name="crm_events")
    op.drop_index("ix_crm_events_event_type", table_name="crm_events")
    op.drop_index("ix_crm_events_created_at", table_name="crm_events")
    op.drop_index("idx_crm_queue_polling", table_name="crm_events")
    op.drop_table("crm_events")

    op.drop_index("idx_alert_suppression", table_name="churn_alerts")
    op.drop_index("idx_alert_ops_dashboard", table_name="churn_alerts")
    op.drop_index("idx_alert_delivery", table_name="churn_alerts")
    op.drop_table("churn_alerts")
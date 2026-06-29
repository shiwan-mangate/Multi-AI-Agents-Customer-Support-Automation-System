"""
create proactive tables

Revision ID: a8c3f1b2d9e7
Revises: 5bfb7b38709d
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "a8c3f1b2d9e7"
down_revision = "5bfb7b38709d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create proactive agent tables.
    """

    # ====================================================
    # proactive_outreach_registry
    # ====================================================

    op.create_table(
        "proactive_outreach_registry",

        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
            primary_key=True,
        ),

        sa.Column(
            "workflow_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "signal_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "customer_id",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "signal_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "decision",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_proactive_customer_signal",
        "proactive_outreach_registry",
        ["customer_id", "signal_type"],
        unique=False,
    )

    op.create_index(
        "idx_proactive_expires_at",
        "proactive_outreach_registry",
        ["expires_at"],
        unique=False,
    )

    # ====================================================
    # proactive_events
    # ====================================================

    op.create_table(
        "proactive_events",

        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
            primary_key=True,
        ),

        sa.Column(
            "workflow_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "signal_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "customer_id",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "signal_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "risk_level",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "decision",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "crm_event_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_proactive_events_customer",
        "proactive_events",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        "idx_proactive_events_signal",
        "proactive_events",
        ["signal_type"],
        unique=False,
    )

    op.create_index(
        "idx_proactive_events_created",
        "proactive_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """
    Rollback proactive tables.
    """

    op.drop_index(
        "idx_proactive_events_created",
        table_name="proactive_events",
    )

    op.drop_index(
        "idx_proactive_events_signal",
        table_name="proactive_events",
    )

    op.drop_index(
        "idx_proactive_events_customer",
        table_name="proactive_events",
    )

    op.drop_table("proactive_events")

    op.drop_index(
        "idx_proactive_expires_at",
        table_name="proactive_outreach_registry",
    )

    op.drop_index(
        "idx_proactive_customer_signal",
        table_name="proactive_outreach_registry",
    )

    op.drop_table("proactive_outreach_registry")
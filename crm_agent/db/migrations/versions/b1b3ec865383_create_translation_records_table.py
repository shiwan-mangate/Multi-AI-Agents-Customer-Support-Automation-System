"""create_translation_records_table

Revision ID: b1b3ec865383
Revises: a8c3f1b2d9e7
Create Date: 2026-06-07 13:12:05.808300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1b3ec865383'
down_revision: Union[str, Sequence[str], None] = 'a8c3f1b2d9e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('translation_records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ticket_id', sa.String(length=100), nullable=False),
    sa.Column('customer_id', sa.String(length=100), nullable=False),
    sa.Column('original_text', sa.Text(), nullable=False),
    sa.Column('original_language', sa.String(length=10), nullable=False),
    sa.Column('english_text', sa.Text(), nullable=False),
    sa.Column('response_english', sa.Text(), nullable=True),
    sa.Column('response_translated', sa.Text(), nullable=True),
    sa.Column('response_language', sa.String(length=10), nullable=True),
    sa.Column('translation_service', sa.String(length=50), nullable=False),
    sa.Column('translation_success', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_translation_records_created_at'), 'translation_records', ['created_at'], unique=False)
    op.create_index(op.f('ix_translation_records_customer_id'), 'translation_records', ['customer_id'], unique=False)
    op.create_index(op.f('ix_translation_records_original_language'), 'translation_records', ['original_language'], unique=False)
    op.create_index(op.f('ix_translation_records_response_language'), 'translation_records', ['response_language'], unique=False)
    op.create_index(op.f('ix_translation_records_ticket_id'), 'translation_records', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_translation_records_translation_success'), 'translation_records', ['translation_success'], unique=False)
   


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_translation_records_translation_success'), table_name='translation_records')
    op.drop_index(op.f('ix_translation_records_ticket_id'), table_name='translation_records')
    op.drop_index(op.f('ix_translation_records_response_language'), table_name='translation_records')
    op.drop_index(op.f('ix_translation_records_original_language'), table_name='translation_records')
    op.drop_index(op.f('ix_translation_records_customer_id'), table_name='translation_records')
    op.drop_index(op.f('ix_translation_records_created_at'), table_name='translation_records')
    op.drop_table('translation_records')

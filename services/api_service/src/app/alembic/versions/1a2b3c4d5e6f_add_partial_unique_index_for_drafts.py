"""Add partial unique index for drafts

Revision ID: 1a2b3c4d5e6f
Revises: 2b8a7c1fde9e
Create Date: 2025-10-02 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '1a2b3c4d5e6f'
down_revision: str | None = '2b8a7c1fde9e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    print('Dropping the old unique index on telegram_id...')
    op.drop_index(op.f('ix_applications_telegram_id'), table_name='applications')

    print("Creating a new partial unique index for applications with status='draft'...")
    op.create_index(
        'ix_unique_draft_per_user',
        'applications',
        ['telegram_id'],
        unique=True,
        postgresql_where=sa.text("status = 'draft'"),
    )
    print('Migration upgrade complete.')


def downgrade() -> None:
    print('Dropping the new partial unique index...')
    op.drop_index('ix_unique_draft_per_user', table_name='applications')

    print('Re-creating the old unique index on telegram_id...')
    op.create_index(
        op.f('ix_applications_telegram_id'), 'applications', ['telegram_id'], unique=True
    )
    print('Migration downgrade complete.')

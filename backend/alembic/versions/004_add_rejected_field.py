"""add rejected field to psychologists

Revision ID: 004
Revises: 003
Create Date: 2025-01-27 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campo rejected ao psychologists
    op.add_column('psychologists', sa.Column('rejected', sa.Boolean(), nullable=True, server_default='0'))


def downgrade() -> None:
    # Remover campo rejected
    op.drop_column('psychologists', 'rejected')


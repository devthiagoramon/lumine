"""add new models

Revision ID: 003
Revises: 002
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campo balance ao psychologists
    op.add_column('psychologists', sa.Column('balance', sa.Float(), nullable=True))
    
    # Adicionar campo rejection_reason ao appointments
    op.add_column('appointments', sa.Column('rejection_reason', sa.Text(), nullable=True))
    
    # Criar tabela de notificações
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('related_id', sa.Integer(), nullable=True),
        sa.Column('related_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    
    # Criar tabela de questionários
    op.create_table(
        'questionnaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_1', sa.Integer(), nullable=True),
        sa.Column('question_2', sa.Integer(), nullable=True),
        sa.Column('question_3', sa.Integer(), nullable=True),
        sa.Column('question_4', sa.Integer(), nullable=True),
        sa.Column('question_5', sa.Integer(), nullable=True),
        sa.Column('question_6', sa.Integer(), nullable=True),
        sa.Column('question_7', sa.Integer(), nullable=True),
        sa.Column('question_8', sa.Integer(), nullable=True),
        sa.Column('question_9', sa.Integer(), nullable=True),
        sa.Column('question_10', sa.Integer(), nullable=True),
        sa.Column('total_score', sa.Integer(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela de pré-cadastro
    op.create_table(
        'psychologist_pre_registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('crp', sa.String(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('consultation_price', sa.Float(), nullable=True),
        sa.Column('online_consultation', sa.Boolean(), nullable=True),
        sa.Column('in_person_consultation', sa.Boolean(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('zip_code', sa.String(), nullable=True),
        sa.Column('specialty_ids', sa.String(), nullable=True),
        sa.Column('approach_ids', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('crp')
    )
    
    # Criar tabela de saques
    op.create_table(
        'withdrawals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('psychologist_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('bank_name', sa.String(), nullable=False),
        sa.Column('bank_account', sa.String(), nullable=False),
        sa.Column('bank_agency', sa.String(), nullable=False),
        sa.Column('account_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['psychologist_id'], ['psychologists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('withdrawals')
    op.drop_table('psychologist_pre_registrations')
    op.drop_table('questionnaires')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_column('appointments', 'rejection_reason')
    op.drop_column('psychologists', 'balance')


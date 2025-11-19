"""seed mock data

Revision ID: 002
Revises: 001
Create Date: 2025-01-27 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime, timedelta
import random

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabelas temporárias para inserção de dados
    users_table = table(
        'users',
        column('id', sa.Integer),
        column('email', sa.String),
        column('hashed_password', sa.String),
        column('full_name', sa.String),
        column('phone', sa.String),
        column('is_active', sa.Boolean),
        column('is_psychologist', sa.Boolean),
        column('is_admin', sa.Boolean),
        column('created_at', sa.DateTime)
    )
    
    specialties_table = table(
        'specialties',
        column('id', sa.Integer),
        column('name', sa.String),
        column('description', sa.Text)
    )
    
    approaches_table = table(
        'approaches',
        column('id', sa.Integer),
        column('name', sa.String),
        column('description', sa.Text)
    )
    
    psychologists_table = table(
        'psychologists',
        column('id', sa.Integer),
        column('user_id', sa.Integer),
        column('crp', sa.String),
        column('bio', sa.Text),
        column('experience_years', sa.Integer),
        column('consultation_price', sa.Float),
        column('online_consultation', sa.Boolean),
        column('in_person_consultation', sa.Boolean),
        column('address', sa.String),
        column('city', sa.String),
        column('state', sa.String),
        column('zip_code', sa.String),
        column('profile_picture', sa.String),
        column('rating', sa.Float),
        column('total_reviews', sa.Integer),
        column('is_verified', sa.Boolean),
        column('created_at', sa.DateTime)
    )
    
    # Inserir especialidades
    op.bulk_insert(specialties_table, [
        {'name': 'Ansiedade', 'description': 'Tratamento de transtornos de ansiedade'},
        {'name': 'Depressão', 'description': 'Tratamento de depressão e transtornos do humor'},
        {'name': 'TDAH', 'description': 'Transtorno de Déficit de Atenção e Hiperatividade'},
        {'name': 'TOC', 'description': 'Transtorno Obsessivo Compulsivo'},
        {'name': 'Trauma', 'description': 'Tratamento de traumas e TEPT'},
        {'name': 'Relacionamentos', 'description': 'Terapia de casal e relacionamentos'},
        {'name': 'Autoestima', 'description': 'Desenvolvimento pessoal e autoestima'},
        {'name': 'Luto', 'description': 'Processamento de luto e perdas'},
        {'name': 'Estresse', 'description': 'Gerenciamento de estresse'},
        {'name': 'Infantil', 'description': 'Psicologia infantil'},
    ])
    
    # Inserir abordagens
    op.bulk_insert(approaches_table, [
        {'name': 'TCC', 'description': 'Terapia Cognitivo-Comportamental'},
        {'name': 'Psicanálise', 'description': 'Abordagem psicanalítica'},
        {'name': 'Humanista', 'description': 'Abordagem humanista'},
        {'name': 'Gestalt', 'description': 'Terapia Gestalt'},
        {'name': 'Comportamental', 'description': 'Análise do Comportamento'},
        {'name': 'Sistêmica', 'description': 'Terapia Sistêmica'},
        {'name': 'Fenomenológica', 'description': 'Abordagem fenomenológica'},
        {'name': 'Integrativa', 'description': 'Abordagem integrativa'},
    ])
    
    # Nota: A inserção de usuários e psicólogos com senhas hashadas
    # deve ser feita via script Python devido à necessidade de hash de senha
    # Esta migration apenas cria a estrutura


def downgrade() -> None:
    # Remover dados mockados
    op.execute("DELETE FROM psychologist_availability")
    op.execute("DELETE FROM payments")
    op.execute("DELETE FROM emotion_diaries")
    op.execute("DELETE FROM forum_comments")
    op.execute("DELETE FROM forum_posts")
    op.execute("DELETE FROM appointments")
    op.execute("DELETE FROM reviews")
    op.execute("DELETE FROM psychologist_approaches")
    op.execute("DELETE FROM psychologist_specialties")
    op.execute("DELETE FROM favorites")
    op.execute("DELETE FROM psychologists")
    op.execute("DELETE FROM users WHERE is_admin = 0")
    op.execute("DELETE FROM approaches")
    op.execute("DELETE FROM specialties")


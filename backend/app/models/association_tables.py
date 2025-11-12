"""
Tabelas de associação (many-to-many)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from app.database import Base

# Tabela de associação para favoritos
favorites = Table(
    'favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('psychologist_id', Integer, ForeignKey('psychologists.id'), primary_key=True)
)

# Tabela de associação para especialidades
psychologist_specialties = Table(
    'psychologist_specialties',
    Base.metadata,
    Column('psychologist_id', Integer, ForeignKey('psychologists.id')),
    Column('specialty_id', Integer, ForeignKey('specialties.id'))
)

# Tabela de associação para abordagens
psychologist_approaches = Table(
    'psychologist_approaches',
    Base.metadata,
    Column('psychologist_id', Integer, ForeignKey('psychologists.id')),
    Column('approach_id', Integer, ForeignKey('approaches.id'))
)


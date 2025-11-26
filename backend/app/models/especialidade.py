"""
Specialty Model
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship, Session
from typing import List
from app.database import Base, get_db_session
from app.models.tabelas_associacao import psychologist_specialties

class Specialty(Base):
    __tablename__ = "specialties"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column("name", String, unique=True, nullable=False)
    descricao = Column("description", Text)
    
    psychologists = relationship("Psychologist", secondary=psychologist_specialties, back_populates="specialties")
    
    # Métodos de acesso ao banco
    @classmethod
    def listar_todos(cls) -> List["Specialty"]:
        """Listar todas as especialidades"""
        db = get_db_session()
        try:
            return db.query(cls).all()
        finally:
            db.close()
    
    @classmethod
    def obter_por_ids(cls, ids: List[int]) -> List["Specialty"]:
        """Obter especialidades por lista de IDs"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id.in_(ids)).all()
        finally:
            db.close()


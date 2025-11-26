"""
PsychologistAvailability Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class PsychologistAvailability(Base):
    __tablename__ = "psychologist_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    id_psicologo = Column("psychologist_id", Integer, ForeignKey("psychologists.id"), nullable=False)
    dia_da_semana = Column("day_of_week", Integer, nullable=False)  # 0=Segunda, 1=Terça, ..., 6=Domingo
    horario_inicio = Column("start_time", String, nullable=False)  # Formato HH:MM
    horario_fim = Column("end_time", String, nullable=False)  # Formato HH:MM
    esta_disponivel = Column("is_available", Boolean, default=True)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[id_psicologo], back_populates="availability", overlaps="availability")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_disponibilidade: int, id_psicologo: Optional[int] = None) -> Optional["PsychologistAvailability"]:
        """Obter disponibilidade por ID"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id == id_disponibilidade)
            if id_psicologo:
                query = query.filter(cls.id_psicologo == id_psicologo)
            return query.first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, id_psicologo: int, apenas_disponiveis: bool = False) -> List["PsychologistAvailability"]:
        """Listar disponibilidades de um psicólogo"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id_psicologo == id_psicologo)
            if apenas_disponiveis:
                query = query.filter(cls.esta_disponivel == True)
            return query.order_by(cls.dia_da_semana).all()
        finally:
            db.close()
    
    @classmethod
    def verificar_existente(cls, id_psicologo: int, dia_da_semana: int) -> Optional["PsychologistAvailability"]:
        """Verificar se já existe disponibilidade para um dia da semana"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id_psicologo == id_psicologo,
                cls.dia_da_semana == dia_da_semana
            ).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "PsychologistAvailability":
        """Criar nova disponibilidade"""
        db = get_db_session()
        try:
            disponibilidade = cls(**kwargs)
            db.add(disponibilidade)
            db.commit()
            db.refresh(disponibilidade)
            return disponibilidade
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "PsychologistAvailability":
        """Atualizar disponibilidade"""
        db = get_db_session()
        try:
            disponibilidade = db.query(PsychologistAvailability).filter(PsychologistAvailability.id == self.id).first()
            if not disponibilidade:
                raise ValueError("Disponibilidade não encontrada")
            
            for key, value in kwargs.items():
                if hasattr(disponibilidade, key):
                    setattr(disponibilidade, key, value)
            db.commit()
            db.refresh(disponibilidade)
            return disponibilidade
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar disponibilidade"""
        db = get_db_session()
        try:
            disponibilidade = db.query(PsychologistAvailability).filter(PsychologistAvailability.id == self.id).first()
            if disponibilidade:
                db.delete(disponibilidade)
                db.commit()
        finally:
            db.close()


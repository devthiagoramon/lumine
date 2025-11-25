"""
Appointment Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime
from app.database import Base, get_db_session

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    id_psicologo = Column("psychologist_id", Integer, ForeignKey("psychologists.id"), nullable=False)
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    data_agendamento = Column("appointment_date", DateTime(timezone=True), nullable=False)
    tipo_agendamento = Column("appointment_type", String, nullable=False)  # 'online' ou 'presencial'
    status = Column(String, default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed', 'rejected'
    motivo_recusa = Column("rejection_reason", Text)  # Motivo da recusa pelo psicólogo
    observacoes = Column("notes", Text)
    status_pagamento = Column("payment_status", String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    id_pagamento = Column("payment_id", String)  # ID do pagamento mockado
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[id_psicologo], back_populates="appointments", overlaps="appointments")
    user = relationship("User", foreign_keys=[id_usuario], back_populates="appointments", overlaps="appointments")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_agendamento: int, carregar_relacionamentos: bool = False) -> Optional["Appointment"]:
        """Obter agendamento por ID"""
        db = get_db_session()
        try:
            query = db.query(cls)
            if carregar_relacionamentos:
                from app.models.psychologist import Psychologist
                query = query.options(
                    joinedload(cls.psychologist).joinedload(Psychologist.user),
                    joinedload(cls.psychologist).joinedload(Psychologist.specialties),
                    joinedload(cls.psychologist).joinedload(Psychologist.approaches),
                    joinedload(cls.user)
                )
            return query.filter(cls.id == id_agendamento).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, id_usuario: int, status: Optional[str] = None) -> List["Appointment"]:
        """Listar agendamentos de um usuário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id_usuario == id_usuario)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.data_agendamento.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, id_psicologo: int, status: Optional[str] = None) -> List["Appointment"]:
        """Listar agendamentos de um psicólogo"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id_psicologo == id_psicologo)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.data_agendamento.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo_e_periodo(cls, id_psicologo: int, data_inicio: datetime, data_fim: datetime) -> List["Appointment"]:
        """Listar agendamentos de um psicólogo em um período"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id_psicologo == id_psicologo,
                cls.data_agendamento >= data_inicio,
                cls.data_agendamento <= data_fim,
                cls.status.in_(['pending', 'confirmed'])
            ).all()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Appointment":
        """Criar novo agendamento"""
        db = get_db_session()
        try:
            agendamento = cls(**kwargs)
            db.add(agendamento)
            db.commit()
            db.refresh(agendamento)
            return agendamento
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Appointment":
        """Atualizar agendamento"""
        db = get_db_session()
        try:
            agendamento = db.query(Appointment).filter(Appointment.id == self.id).first()
            if not agendamento:
                raise ValueError("Agendamento não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(agendamento, key):
                    setattr(agendamento, key, value)
            db.commit()
            db.refresh(agendamento)
            return agendamento
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar agendamento"""
        db = get_db_session()
        try:
            agendamento = db.query(Appointment).filter(Appointment.id == self.id).first()
            if agendamento:
                db.delete(agendamento)
                db.commit()
        finally:
            db.close()


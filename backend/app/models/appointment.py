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
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    appointment_type = Column(String, nullable=False)  # 'online' ou 'presencial'
    status = Column(String, default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed', 'rejected'
    rejection_reason = Column(Text)  # Motivo da recusa pelo psicólogo
    notes = Column(Text)
    payment_status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    payment_id = Column(String)  # ID do pagamento mockado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[psychologist_id], back_populates="appointments", overlaps="appointments")
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments", overlaps="appointments")
    
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
    def listar_por_usuario(cls, user_id: int, status: Optional[str] = None) -> List["Appointment"]:
        """Listar agendamentos de um usuário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.user_id == user_id)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.appointment_date.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, psychologist_id: int, status: Optional[str] = None) -> List["Appointment"]:
        """Listar agendamentos de um psicólogo"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.psychologist_id == psychologist_id)
            if status:
                query = query.filter(cls.status == status)
            return query.order_by(cls.appointment_date.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo_e_periodo(cls, psychologist_id: int, data_inicio: datetime, data_fim: datetime) -> List["Appointment"]:
        """Listar agendamentos de um psicólogo em um período"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.psychologist_id == psychologist_id,
                cls.appointment_date >= data_inicio,
                cls.appointment_date <= data_fim,
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


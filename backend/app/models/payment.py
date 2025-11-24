"""
Payment Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # 'credit_card', 'debit_card', 'pix', 'boleto'
    status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    payment_id = Column(String, unique=True)  # ID do pagamento mockado
    transaction_id = Column(String)  # ID da transação mockada
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    appointment = relationship("Appointment", foreign_keys=[appointment_id])
    user = relationship("User", foreign_keys=[user_id], back_populates="payments", overlaps="payments")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_pagamento: int) -> Optional["Payment"]:
        """Obter pagamento por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id == id_pagamento).first()
        finally:
            db.close()
    
    @classmethod
    def obter_por_agendamento(cls, id_agendamento: int) -> Optional["Payment"]:
        """Obter pagamento por agendamento"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.appointment_id == id_agendamento).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, id_usuario: int) -> List["Payment"]:
        """Listar pagamentos de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.user_id == id_usuario).order_by(cls.created_at.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Payment":
        """Criar novo pagamento"""
        db = get_db_session()
        try:
            pagamento = cls(**kwargs)
            db.add(pagamento)
            db.commit()
            db.refresh(pagamento)
            return pagamento
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Payment":
        """Atualizar pagamento"""
        db = get_db_session()
        try:
            pagamento = db.query(Payment).filter(Payment.id == self.id).first()
            if not pagamento:
                raise ValueError("Pagamento não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(pagamento, key):
                    setattr(pagamento, key, value)
            db.commit()
            db.refresh(pagamento)
            return pagamento
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar pagamento"""
        db = get_db_session()
        try:
            pagamento = db.query(Payment).filter(Payment.id == self.id).first()
            if pagamento:
                db.delete(pagamento)
                db.commit()
        finally:
            db.close()


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
    id_agendamento = Column("appointment_id", Integer, ForeignKey("appointments.id"), nullable=False)
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    valor = Column("amount", Float, nullable=False)
    metodo_pagamento = Column("payment_method", String, nullable=False)  # 'credit_card', 'debit_card', 'pix', 'boleto'
    status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    id_pagamento = Column("payment_id", String, unique=True)  # ID do pagamento mockado
    id_transacao = Column("transaction_id", String)  # ID da transação mockada
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    appointment = relationship("Appointment", foreign_keys=[id_agendamento])
    user = relationship("User", foreign_keys=[id_usuario], back_populates="payments", overlaps="payments")
    
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
            return db.query(cls).filter(cls.id_agendamento == id_agendamento).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, id_usuario: int) -> List["Payment"]:
        """Listar pagamentos de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id_usuario == id_usuario).order_by(cls.criado_em.desc()).all()
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


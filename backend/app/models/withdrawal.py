"""
Withdrawal Model
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class Withdrawal(Base):
    __tablename__ = "withdrawals"
    
    id = Column(Integer, primary_key=True, index=True)
    id_psicologo = Column("psychologist_id", Integer, ForeignKey("psychologists.id"), nullable=False)
    valor = Column("amount", Float, nullable=False)
    nome_banco = Column("bank_name", String, nullable=False)
    conta_bancaria = Column("bank_account", String, nullable=False)
    agencia = Column("bank_agency", String, nullable=False)
    tipo_conta = Column("account_type", String, nullable=False)  # 'checking', 'savings'
    status = Column(String, default='pending')  # 'pending', 'processing', 'completed', 'rejected'
    motivo_recusa = Column("rejection_reason", Text)
    processado_em = Column("processed_at", DateTime(timezone=True))
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[id_psicologo], back_populates="withdrawals", overlaps="withdrawals")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_saque: int, id_psicologo: Optional[int] = None) -> Optional["Withdrawal"]:
        """Obter saque por ID"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id == id_saque)
            if id_psicologo:
                query = query.filter(cls.id_psicologo == id_psicologo)
            return query.first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, id_psicologo: int) -> List["Withdrawal"]:
        """Listar saques de um psicólogo"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id_psicologo == id_psicologo
            ).order_by(cls.criado_em.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Withdrawal":
        """Criar novo saque"""
        db = get_db_session()
        try:
            saque = cls(**kwargs)
            db.add(saque)
            db.commit()
            db.refresh(saque)
            return saque
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Withdrawal":
        """Atualizar saque"""
        db = get_db_session()
        try:
            saque = db.query(Withdrawal).filter(Withdrawal.id == self.id).first()
            if not saque:
                raise ValueError("Saque não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(saque, key):
                    setattr(saque, key, value)
            db.commit()
            db.refresh(saque)
            return saque
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar saque"""
        db = get_db_session()
        try:
            saque = db.query(Withdrawal).filter(Withdrawal.id == self.id).first()
            if saque:
                db.delete(saque)
                db.commit()
        finally:
            db.close()


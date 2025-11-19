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
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    amount = Column(Float, nullable=False)
    bank_name = Column(String, nullable=False)
    bank_account = Column(String, nullable=False)
    bank_agency = Column(String, nullable=False)
    account_type = Column(String, nullable=False)  # 'checking', 'savings'
    status = Column(String, default='pending')  # 'pending', 'processing', 'completed', 'rejected'
    rejection_reason = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[psychologist_id], back_populates="withdrawals", overlaps="withdrawals")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_saque: int, psychologist_id: Optional[int] = None) -> Optional["Withdrawal"]:
        """Obter saque por ID"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id == id_saque)
            if psychologist_id:
                query = query.filter(cls.psychologist_id == psychologist_id)
            return query.first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, psychologist_id: int) -> List["Withdrawal"]:
        """Listar saques de um psicólogo"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.psychologist_id == psychologist_id
            ).order_by(cls.created_at.desc()).all()
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


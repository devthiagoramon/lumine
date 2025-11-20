"""
Payment Method Model - Métodos de pagamento salvos pelo usuário
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_type = Column(String, nullable=False)  # 'credit_card', 'debit_card'
    card_brand = Column(String)  # 'visa', 'mastercard', 'amex', 'elo', etc.
    last_four_digits = Column(String(4), nullable=False)  # Últimos 4 dígitos
    card_holder = Column(String, nullable=False)  # Nome do portador
    expiry_month = Column(String(2), nullable=False)  # MM
    expiry_year = Column(String(4), nullable=False)  # YYYY
    is_default = Column(Boolean, default=False)  # Método padrão
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_metodo: int) -> Optional["PaymentMethod"]:
        """Obter método de pagamento por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id == id_metodo).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, user_id: int) -> List["PaymentMethod"]:
        """Listar métodos de pagamento de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.user_id == user_id).order_by(
                cls.is_default.desc(), cls.created_at.desc()
            ).all()
        finally:
            db.close()
    
    @classmethod
    def obter_padrao(cls, user_id: int) -> Optional["PaymentMethod"]:
        """Obter método de pagamento padrão do usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.user_id == user_id,
                cls.is_default == True
            ).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "PaymentMethod":
        """Criar novo método de pagamento"""
        db = get_db_session()
        try:
            # Se este for marcado como padrão, remover padrão dos outros
            if kwargs.get('is_default', False):
                cls.remover_padrao(kwargs['user_id'])
            
            metodo = cls(**kwargs)
            db.add(metodo)
            db.commit()
            db.refresh(metodo)
            return metodo
        finally:
            db.close()
    
    @classmethod
    def remover_padrao(cls, user_id: int) -> None:
        """Remover flag de padrão de todos os métodos do usuário"""
        db = get_db_session()
        try:
            db.query(cls).filter(
                cls.user_id == user_id,
                cls.is_default == True
            ).update({"is_default": False})
            db.commit()
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "PaymentMethod":
        """Atualizar método de pagamento"""
        db = get_db_session()
        try:
            metodo = db.query(PaymentMethod).filter(PaymentMethod.id == self.id).first()
            if not metodo:
                raise ValueError("Método de pagamento não encontrado")
            
            # Se está sendo marcado como padrão, remover padrão dos outros
            if kwargs.get('is_default', False) and not metodo.is_default:
                PaymentMethod.remover_padrao(metodo.user_id)
            
            for key, value in kwargs.items():
                if hasattr(metodo, key):
                    setattr(metodo, key, value)
            
            db.commit()
            db.refresh(metodo)
            return metodo
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar método de pagamento"""
        db = get_db_session()
        try:
            metodo = db.query(PaymentMethod).filter(PaymentMethod.id == self.id).first()
            if metodo:
                db.delete(metodo)
                db.commit()
        finally:
            db.close()


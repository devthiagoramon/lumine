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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    tipo_cartao = Column("card_type", String, nullable=False)  # 'credit_card', 'debit_card'
    bandeira = Column("card_brand", String)  # 'visa', 'mastercard', 'amex', 'elo', etc.
    ultimos_quatro_digitos = Column("last_four_digits", String(4), nullable=False)  # Últimos 4 dígitos
    portador = Column("card_holder", String, nullable=False)  # Nome do portador
    mes_validade = Column("expiry_month", String(2), nullable=False)  # MM
    ano_validade = Column("expiry_year", String(4), nullable=False)  # YYYY
    eh_padrao = Column("is_default", Boolean, default=False)  # Método padrão
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario])
    
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
    def listar_por_usuario(cls, id_usuario: int) -> List["PaymentMethod"]:
        """Listar métodos de pagamento de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id_usuario == id_usuario).order_by(
                cls.eh_padrao.desc(), cls.criado_em.desc()
            ).all()
        finally:
            db.close()
    
    @classmethod
    def obter_padrao(cls, id_usuario: int) -> Optional["PaymentMethod"]:
        """Obter método de pagamento padrão do usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id_usuario == id_usuario,
                cls.eh_padrao == True
            ).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "PaymentMethod":
        """Criar novo método de pagamento"""
        db = get_db_session()
        try:
            # Mapear campos em inglês para português se necessário
            mapped_kwargs = {}
            field_mapping = {
                'user_id': 'id_usuario',
                'card_type': 'tipo_cartao',
                'card_brand': 'bandeira',
                'last_four_digits': 'ultimos_quatro_digitos',
                'card_holder': 'portador',
                'expiry_month': 'mes_validade',
                'expiry_year': 'ano_validade',
                'is_default': 'eh_padrao'
            }
            
            for key, value in kwargs.items():
                mapped_key = field_mapping.get(key, key)
                mapped_kwargs[mapped_key] = value
            
            # Se este for marcado como padrão, remover padrão dos outros
            if mapped_kwargs.get('eh_padrao', False):
                id_user = mapped_kwargs.get('id_usuario')
                if id_user:
                    cls.remover_padrao(id_user)
            
            metodo = cls(**mapped_kwargs)
            db.add(metodo)
            db.commit()
            db.refresh(metodo)
            return metodo
        finally:
            db.close()
    
    @classmethod
    def remover_padrao(cls, id_usuario: int) -> None:
        """Remover flag de padrão de todos os métodos do usuário"""
        db = get_db_session()
        try:
            db.query(cls).filter(
                cls.id_usuario == id_usuario,
                cls.eh_padrao == True
            ).update({"eh_padrao": False})
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
            if kwargs.get('eh_padrao', False) and not metodo.eh_padrao:
                PaymentMethod.remover_padrao(metodo.id_usuario)
            
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


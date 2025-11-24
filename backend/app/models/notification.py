"""
Notification Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session
from typing import Optional, List
from app.database import Base, get_db_session

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 'appointment', 'payment', 'review', 'system', etc.
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)  # ID do recurso relacionado (appointment_id, payment_id, etc.)
    related_type = Column(String)  # Tipo do recurso relacionado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications", overlaps="notifications")
    
    # Métodos de acesso ao banco
    @classmethod
    def listar_por_usuario(
        cls,
        id_usuario: int,
        lida: Optional[bool] = None,
        limite: int = 50
    ) -> List["Notification"]:
        """Listar notificações de um usuário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.user_id == id_usuario)
            
            if lida is not None:
                query = query.filter(cls.is_read == lida)
            
            return query.order_by(cls.created_at.desc()).limit(limite).all()
        finally:
            db.close()
    
    @classmethod
    def contar_nao_lidas(cls, id_usuario: int) -> int:
        """Contar notificações não lidas de um usuário"""
        db = get_db_session()
        try:
            return db.query(func.count(cls.id)).filter(
                cls.user_id == id_usuario,
                cls.is_read == False
            ).scalar()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Notification":
        """Criar nova notificação"""
        db = get_db_session()
        try:
            notificacao = cls(**kwargs)
            db.add(notificacao)
            db.commit()
            db.refresh(notificacao)
            return notificacao
        finally:
            db.close()
    
    def marcar_como_lida(self) -> "Notification":
        """Marcar notificação como lida"""
        db = get_db_session()
        try:
            notificacao = db.query(Notification).filter(Notification.id == self.id).first()
            if notificacao:
                notificacao.is_read = True
                db.commit()
                db.refresh(notificacao)
                return notificacao
            return self
        finally:
            db.close()
    
    @classmethod
    def marcar_todas_como_lidas(cls, id_usuario: int) -> int:
        """Marcar todas as notificações de um usuário como lidas"""
        db = get_db_session()
        try:
            atualizadas = db.query(cls).filter(
                cls.user_id == id_usuario,
                cls.is_read == False
            ).update({"is_read": True})
            db.commit()
            return atualizadas
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar notificação"""
        db = get_db_session()
        try:
            notificacao = db.query(Notification).filter(Notification.id == self.id).first()
            if notificacao:
                db.delete(notificacao)
                db.commit()
        finally:
            db.close()


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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    titulo = Column("title", String, nullable=False)
    mensagem = Column("message", Text, nullable=False)
    tipo = Column("type", String, nullable=False)  # 'appointment', 'payment', 'review', 'system', etc.
    foi_lida = Column("is_read", Boolean, default=False)
    id_relacionado = Column("related_id", Integer)  # ID do recurso relacionado (appointment_id, payment_id, etc.)
    tipo_relacionado = Column("related_type", String)  # Tipo do recurso relacionado
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario], back_populates="notifications", overlaps="notifications")
    
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
            query = db.query(cls).filter(cls.id_usuario == id_usuario)
            
            if lida is not None:
                query = query.filter(cls.foi_lida == lida)
            
            return query.order_by(cls.criado_em.desc()).limit(limite).all()
        finally:
            db.close()
    
    @classmethod
    def contar_nao_lidas(cls, id_usuario: int) -> int:
        """Contar notificações não lidas de um usuário"""
        db = get_db_session()
        try:
            return db.query(func.count(cls.id)).filter(
                cls.id_usuario == id_usuario,
                cls.foi_lida == False
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
                notificacao.foi_lida = True
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
                cls.id_usuario == id_usuario,
                cls.foi_lida == False
            ).update({"foi_lida": True})
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


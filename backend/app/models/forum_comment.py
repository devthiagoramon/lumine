"""
ForumComment Model
"""
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class ForumComment(Base):
    __tablename__ = "forum_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    id_post = Column("post_id", Integer, ForeignKey("forum_posts.id"), nullable=False)
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    conteudo = Column("content", Text, nullable=False)
    eh_anonimo = Column("is_anonymous", Boolean, default=False)
    curtidas = Column("likes", Integer, default=0)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    post = relationship("ForumPost", back_populates="comments")
    user = relationship("User", foreign_keys=[id_usuario], back_populates="forum_comments", overlaps="forum_comments")
    
    # Métodos de acesso ao banco
    @classmethod
    def listar_por_post(cls, id_post: int) -> List["ForumComment"]:
        """Listar comentários de um post"""
        db = get_db_session()
        try:
            return db.query(cls).options(
                joinedload(cls.user)
            ).filter(cls.id_post == id_post).order_by(cls.criado_em.asc()).all()
        finally:
            db.close()
    
    @classmethod
    def obter_por_id_com_relacionamentos(cls, id_comentario: int) -> Optional["ForumComment"]:
        """Obter comentário por ID com relacionamentos"""
        db = get_db_session()
        try:
            return db.query(cls).options(joinedload(cls.user)).filter(cls.id == id_comentario).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "ForumComment":
        """Criar novo comentário"""
        db = get_db_session()
        try:
            comentario = cls(**kwargs)
            db.add(comentario)
            db.commit()
            db.refresh(comentario)
            return comentario
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "ForumComment":
        """Atualizar comentário"""
        db = get_db_session()
        try:
            comentario = db.query(ForumComment).filter(ForumComment.id == self.id).first()
            if not comentario:
                raise ValueError("Comentário não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(comentario, key):
                    setattr(comentario, key, value)
            db.commit()
            db.refresh(comentario)
            return comentario
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar comentário"""
        db = get_db_session()
        try:
            comentario = db.query(ForumComment).filter(ForumComment.id == self.id).first()
            if comentario:
                db.delete(comentario)
                db.commit()
        finally:
            db.close()


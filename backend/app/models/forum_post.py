"""
ForumPost Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy import desc, or_
from typing import Optional, List
from app.database import Base, get_db_session

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default='geral')  # 'geral', 'ansiedade', 'depressao', 'relacionamentos', etc.
    is_anonymous = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="forum_posts", overlaps="forum_posts")
    comments = relationship("ForumComment", back_populates="post", cascade="all, delete-orphan")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_post: int) -> Optional["ForumPost"]:
        """Obter post por ID"""
        db = get_db_session()
        try:
            post = db.query(cls).options(
                joinedload(cls.user)
            ).filter(cls.id == id_post).first()
            
            if post:
                # Contar comentários
                from app.models.forum_comment import ForumComment
                comments_count = db.query(func.count(ForumComment.id)).filter(
                    ForumComment.post_id == post.id
                ).scalar()
                post.comments_count = comments_count
            
            return post
        finally:
            db.close()
    
    @classmethod
    def listar(
        cls,
        categoria: Optional[str] = None,
        busca: Optional[str] = None,
        pagina: int = 1,
        tamanho_pagina: int = 20
    ) -> List["ForumPost"]:
        """Listar posts do fórum"""
        db = get_db_session()
        try:
            query = db.query(cls).options(joinedload(cls.user))
            
            if categoria:
                query = query.filter(cls.category == categoria)
            
            if busca:
                search_term = f"%{busca}%"
                query = query.filter(
                    or_(
                        cls.title.ilike(search_term),
                        cls.content.ilike(search_term)
                    )
                )
            
            posts = query.order_by(desc(cls.created_at)).offset(
                (pagina - 1) * tamanho_pagina
            ).limit(tamanho_pagina).all()
            
            # Adicionar contagem de comentários
            from app.models.forum_comment import ForumComment
            for post in posts:
                comments_count = db.query(func.count(ForumComment.id)).filter(
                    ForumComment.post_id == post.id
                ).scalar()
                post.comments_count = comments_count
            
            return posts
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "ForumPost":
        """Criar novo post"""
        db = get_db_session()
        try:
            post = cls(**kwargs)
            db.add(post)
            db.commit()
            db.refresh(post)
            return post
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "ForumPost":
        """Atualizar post"""
        db = get_db_session()
        try:
            post = db.query(ForumPost).filter(ForumPost.id == self.id).first()
            if not post:
                raise ValueError("Post não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(post, key):
                    setattr(post, key, value)
            db.commit()
            db.refresh(post)
            return post
        finally:
            db.close()
    
    def incrementar_visualizacao(self) -> "ForumPost":
        """Incrementar contador de visualizações"""
        db = get_db_session()
        try:
            post = db.query(ForumPost).filter(ForumPost.id == self.id).first()
            if post:
                post.views += 1
                db.commit()
                db.refresh(post)
                return post
            return self
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar post"""
        db = get_db_session()
        try:
            post = db.query(ForumPost).filter(ForumPost.id == self.id).first()
            if post:
                db.delete(post)
                db.commit()
        finally:
            db.close()


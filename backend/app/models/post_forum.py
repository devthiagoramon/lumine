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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    titulo = Column("title", String, nullable=False)
    conteudo = Column("content", Text, nullable=False)
    categoria = Column("category", String, default='geral')  # 'geral', 'ansiedade', 'depressao', 'relacionamentos', etc.
    eh_anonimo = Column("is_anonymous", Boolean, default=False)
    visualizacoes = Column("views", Integer, default=0)
    curtidas = Column("likes", Integer, default=0)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario], back_populates="forum_posts", overlaps="forum_posts")
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
                from app.models.comentario_forum import ForumComment
                comments_count = db.query(func.count(ForumComment.id)).filter(
                    ForumComment.id_post == post.id
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
                query = query.filter(cls.categoria == categoria)
            
            if busca:
                search_term = f"%{busca}%"
                query = query.filter(
                    or_(
                        cls.titulo.ilike(search_term),
                        cls.conteudo.ilike(search_term)
                    )
                )
            
            posts = query.order_by(desc(cls.criado_em)).offset(
                (pagina - 1) * tamanho_pagina
            ).limit(tamanho_pagina).all()
            
            # Adicionar contagem de comentários
            from app.models.comentario_forum import ForumComment
            for post in posts:
                comments_count = db.query(func.count(ForumComment.id)).filter(
                    ForumComment.id_post == post.id
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
                post.visualizacoes += 1
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


"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy.sql import func
from typing import Optional
from app.database import Base, get_db_session
from app.models.tabelas_associacao import favorites

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column("hashed_password", String, nullable=False)
    nome_completo = Column("full_name", String, nullable=False)
    telefone = Column("phone", String)
    esta_ativo = Column("is_active", Boolean, default=True)
    eh_psicologo = Column("is_psychologist", Boolean, default=False)
    eh_admin = Column("is_admin", Boolean, default=False)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    psychologist_profile = relationship("Psychologist", back_populates="user", uselist=False)
    favorite_psychologists = relationship("Psychologist", secondary=favorites, backref="favorited_by")
    # Usar foreign_keys apenas quando necessário - o SQLAlchemy pode inferir automaticamente baseado nas foreign keys definidas nos outros modelos
    appointments = relationship("Appointment", back_populates="user", overlaps="appointments")
    reviews = relationship("Review", back_populates="user", overlaps="reviews")
    forum_posts = relationship("ForumPost", back_populates="user", overlaps="forum_posts")
    forum_comments = relationship("ForumComment", back_populates="user", overlaps="forum_comments")
    emotion_diaries = relationship("EmotionDiary", back_populates="user", overlaps="emotion_diaries")
    payments = relationship("Payment", back_populates="user", overlaps="payments")
    notifications = relationship("Notification", back_populates="user", overlaps="notifications")
    questionnaires = relationship("Questionnaire", back_populates="user", overlaps="questionnaires")
    pre_registrations = relationship("PsychologistPreRegistration", back_populates="user", overlaps="pre_registrations")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_usuario: int) -> Optional["User"]:
        """Obter usuário por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id == id_usuario).first()
        finally:
            db.close()
    
    @classmethod
    def obter_por_email(cls, email: str) -> Optional["User"]:
        """Obter usuário por email"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.email == email).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "User":
        """Criar novo usuário"""
        db = get_db_session()
        try:
            usuario = cls(**kwargs)
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "User":
        """Atualizar usuário"""
        db = get_db_session()
        try:
            # Recarregar instância na sessão
            usuario = db.query(User).filter(User.id == self.id).first()
            if not usuario:
                raise ValueError("Usuário não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)
            db.commit()
            db.refresh(usuario)
            return usuario
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar usuário"""
        db = get_db_session()
        try:
            usuario = db.query(User).filter(User.id == self.id).first()
            if usuario:
                db.delete(usuario)
                db.commit()
        finally:
            db.close()
    
    def obter_com_favoritos(self):
        """Obter usuário com relacionamento de favoritos carregado"""
        db = get_db_session()
        try:
            return db.query(User).options(
                joinedload(User.favorite_psychologists)
            ).filter(User.id == self.id).first()
        finally:
            db.close()
    
    def obter_com_favoritos_completo(self):
        """Obter usuário com favoritos e seus relacionamentos completos"""
        from app.models.psicologo import Psychologist
        db = get_db_session()
        try:
            return db.query(User).options(
                joinedload(User.favorite_psychologists).joinedload(Psychologist.user),
                joinedload(User.favorite_psychologists).joinedload(Psychologist.specialties),
                joinedload(User.favorite_psychologists).joinedload(Psychologist.approaches)
            ).filter(User.id == self.id).first()
        finally:
            db.close()
    
    def adicionar_favorito(self, id_psicologo: int) -> None:
        """Adicionar psicólogo aos favoritos"""
        from app.models.psicologo import Psychologist
        db = get_db_session()
        try:
            usuario_db = db.query(User).options(
                joinedload(User.favorite_psychologists)
            ).filter(User.id == self.id).first()
            
            if not usuario_db:
                raise ValueError("Usuário não encontrado")
            
            psicologo = db.query(Psychologist).filter(Psychologist.id == id_psicologo).first()
            if not psicologo:
                raise ValueError("Psicólogo não encontrado")
            
            if psicologo in usuario_db.favorite_psychologists:
                raise ValueError("Psicólogo já está nos favoritos")
            
            usuario_db.favorite_psychologists.append(psicologo)
            db.commit()
        finally:
            db.close()
    
    def remover_favorito(self, id_psicologo: int) -> None:
        """Remover psicólogo dos favoritos"""
        from app.models.psicologo import Psychologist
        db = get_db_session()
        try:
            usuario_db = db.query(User).options(
                joinedload(User.favorite_psychologists)
            ).filter(User.id == self.id).first()
            
            if not usuario_db:
                raise ValueError("Usuário não encontrado")
            
            psicologo = db.query(Psychologist).filter(Psychologist.id == id_psicologo).first()
            if not psicologo:
                raise ValueError("Psicólogo não encontrado")
            
            if psicologo not in usuario_db.favorite_psychologists:
                raise ValueError("Psicólogo não encontrado nos favoritos")
            
            usuario_db.favorite_psychologists.remove(psicologo)
            db.commit()
        finally:
            db.close()


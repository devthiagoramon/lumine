"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy.sql import func
from typing import Optional
from app.database import Base, get_db_session
from app.models.association_tables import favorites

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_psychologist = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    psychologist_profile = relationship("Psychologist", back_populates="user", uselist=False)
    favorite_psychologists = relationship("Psychologist", secondary=favorites, backref="favorited_by")
    appointments = relationship("Appointment", foreign_keys="Appointment.user_id", back_populates="user", overlaps="appointments")
    reviews = relationship("Review", foreign_keys="Review.user_id", back_populates="user", overlaps="reviews")
    forum_posts = relationship("ForumPost", foreign_keys="ForumPost.user_id", back_populates="user", overlaps="forum_posts")
    forum_comments = relationship("ForumComment", foreign_keys="ForumComment.user_id", back_populates="user", overlaps="forum_comments")
    emotion_diaries = relationship("EmotionDiary", foreign_keys="EmotionDiary.user_id", back_populates="user", overlaps="emotion_diaries")
    payments = relationship("Payment", foreign_keys="Payment.user_id", back_populates="user", overlaps="payments")
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user", overlaps="notifications")
    questionnaires = relationship("Questionnaire", foreign_keys="Questionnaire.user_id", back_populates="user", overlaps="questionnaires")
    pre_registrations = relationship("PsychologistPreRegistration", foreign_keys="PsychologistPreRegistration.user_id", back_populates="user", overlaps="pre_registrations")
    
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
        from app.models.psychologist import Psychologist
        db = get_db_session()
        try:
            return db.query(User).options(
                joinedload(User.favorite_psychologists).joinedload(Psychologist.user),
                joinedload(User.favorite_psychologists).joinedload(Psychologist.specialties),
                joinedload(User.favorite_psychologists).joinedload(Psychologist.approaches)
            ).filter(User.id == self.id).first()
        finally:
            db.close()


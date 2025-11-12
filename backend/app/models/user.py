"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
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
    appointments = relationship("Appointment", foreign_keys="Appointment.user_id")
    reviews = relationship("Review", foreign_keys="Review.user_id")
    forum_posts = relationship("ForumPost", foreign_keys="ForumPost.user_id")
    forum_comments = relationship("ForumComment", foreign_keys="ForumComment.user_id")
    emotion_diaries = relationship("EmotionDiary", foreign_keys="EmotionDiary.user_id")
    payments = relationship("Payment", foreign_keys="Payment.user_id")
    notifications = relationship("Notification", foreign_keys="Notification.user_id")
    questionnaires = relationship("Questionnaire", foreign_keys="Questionnaire.user_id")
    pre_registrations = relationship("PsychologistPreRegistration", foreign_keys="PsychologistPreRegistration.user_id")


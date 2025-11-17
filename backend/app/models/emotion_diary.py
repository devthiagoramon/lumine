"""
EmotionDiary Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EmotionDiary(Base):
    __tablename__ = "emotion_diaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    emotion = Column(String, nullable=False)  # 'feliz', 'triste', 'ansioso', 'irritado', 'calmo', etc.
    intensity = Column(Integer, nullable=False)  # 1-10
    notes = Column(Text)
    tags = Column(String)  # Tags separadas por vírgula
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="emotion_diaries", overlaps="emotion_diaries")


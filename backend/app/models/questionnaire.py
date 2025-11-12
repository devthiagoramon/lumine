"""
Questionnaire Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_1 = Column(Integer)  # Resposta 1-5
    question_2 = Column(Integer)
    question_3 = Column(Integer)
    question_4 = Column(Integer)
    question_5 = Column(Integer)
    question_6 = Column(Integer)
    question_7 = Column(Integer)
    question_8 = Column(Integer)
    question_9 = Column(Integer)
    question_10 = Column(Integer)
    total_score = Column(Integer)  # Soma das respostas
    recommendation = Column(Text)  # Recomendação baseada no score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])


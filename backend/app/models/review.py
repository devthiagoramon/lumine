"""
Review Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    psychologist = relationship("Psychologist", back_populates="reviews")
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews", overlaps="reviews")


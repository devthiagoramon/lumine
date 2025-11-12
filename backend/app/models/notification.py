"""
Notification Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 'appointment', 'payment', 'review', 'system', etc.
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)  # ID do recurso relacionado (appointment_id, payment_id, etc.)
    related_type = Column(String)  # Tipo do recurso relacionado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id])


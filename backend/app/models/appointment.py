"""
Appointment Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    appointment_type = Column(String, nullable=False)  # 'online' ou 'presencial'
    status = Column(String, default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed', 'rejected'
    rejection_reason = Column(Text)  # Motivo da recusa pelo psicólogo
    notes = Column(Text)
    payment_status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    payment_id = Column(String)  # ID do pagamento mockado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[psychologist_id])
    user = relationship("User", foreign_keys=[user_id])


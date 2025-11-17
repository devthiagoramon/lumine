"""
Psychologist Model
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.association_tables import psychologist_specialties, psychologist_approaches

class Psychologist(Base):
    __tablename__ = "psychologists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    crp = Column(String, unique=True, nullable=False)  # Conselho Regional de Psicologia
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    consultation_price = Column(Float)
    online_consultation = Column(Boolean, default=True)
    in_person_consultation = Column(Boolean, default=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    profile_picture = Column(String)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    balance = Column(Float, default=0.0)  # Saldo disponível para saque
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="psychologist_profile")
    specialties = relationship("Specialty", secondary=psychologist_specialties, back_populates="psychologists")
    approaches = relationship("Approach", secondary=psychologist_approaches, back_populates="psychologists")
    reviews = relationship("Review", back_populates="psychologist")
    appointments = relationship("Appointment", foreign_keys="Appointment.psychologist_id", back_populates="psychologist", overlaps="appointments")
    availability = relationship("PsychologistAvailability", foreign_keys="PsychologistAvailability.psychologist_id", back_populates="psychologist", overlaps="availability")
    withdrawals = relationship("Withdrawal", foreign_keys="Withdrawal.psychologist_id", back_populates="psychologist", overlaps="withdrawals")


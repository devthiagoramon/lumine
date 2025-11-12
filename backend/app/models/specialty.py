"""
Specialty Model
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.association_tables import psychologist_specialties

class Specialty(Base):
    __tablename__ = "specialties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    psychologists = relationship("Psychologist", secondary=psychologist_specialties, back_populates="specialties")


"""
Approach Model
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.association_tables import psychologist_approaches

class Approach(Base):
    __tablename__ = "approaches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    psychologists = relationship("Psychologist", secondary=psychologist_approaches, back_populates="approaches")


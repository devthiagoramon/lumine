"""
Availability Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PsychologistAvailabilityCreate(BaseModel):
    day_of_week: int  # 0=Segunda, 1=Terça, ..., 6=Domingo
    start_time: str  # Formato HH:MM
    end_time: str  # Formato HH:MM
    is_available: bool = True

class PsychologistAvailabilityUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None

class PsychologistAvailabilityResponse(BaseModel):
    id: int
    psychologist_id: int
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


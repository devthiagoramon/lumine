"""
Pre Registration Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PsychologistPreRegistrationCreate(BaseModel):
    crp: str
    bio: Optional[str] = None
    experience_years: int = 0
    consultation_price: Optional[float] = None
    online_consultation: bool = True
    in_person_consultation: bool = False
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    specialty_ids: List[int] = []
    approach_ids: List[int] = []

class PsychologistPreRegistrationResponse(BaseModel):
    id: int
    user_id: int
    crp: str
    bio: Optional[str]
    experience_years: int
    consultation_price: Optional[float]
    online_consultation: bool
    in_person_consultation: bool
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    status: str
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


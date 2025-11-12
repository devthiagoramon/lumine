"""
Psychologist Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.auth import UserResponse
from app.schemas.specialty import SpecialtyResponse
from app.schemas.approach import ApproachResponse

class PsychologistBase(BaseModel):
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
    profile_picture: Optional[str] = None

class PsychologistCreate(PsychologistBase):
    specialty_ids: List[int] = []
    approach_ids: List[int] = []

class PsychologistUpdate(BaseModel):
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_price: Optional[float] = None
    online_consultation: Optional[bool] = None
    in_person_consultation: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    profile_picture: Optional[str] = None
    specialty_ids: Optional[List[int]] = None
    approach_ids: Optional[List[int]] = None

class PsychologistResponse(PsychologistBase):
    id: int
    user_id: int
    rating: float
    total_reviews: int
    is_verified: bool
    created_at: datetime
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    user: UserResponse
    
    class Config:
        from_attributes = True

class PsychologistListItem(BaseModel):
    id: int
    user_id: int
    crp: str
    bio: Optional[str]
    experience_years: int
    consultation_price: Optional[float]
    online_consultation: bool
    in_person_consultation: bool
    city: Optional[str]
    state: Optional[str]
    profile_picture: Optional[str]
    rating: float
    total_reviews: int
    is_verified: bool
    user: UserResponse
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    
    class Config:
        from_attributes = True


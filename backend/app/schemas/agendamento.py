"""
Appointment Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.autenticacao import UserResponse
from app.schemas.psicologo import PsychologistListItem

class AppointmentCreate(BaseModel):
    psychologist_id: int
    appointment_date: datetime
    appointment_type: str  # 'online' ou 'presencial'
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None  # 'pending', 'confirmed', 'cancelled', 'completed', 'rejected'
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    psychologist_id: int
    user_id: int
    appointment_date: datetime
    appointment_type: str
    status: str
    rejection_reason: Optional[str] = None
    notes: Optional[str]
    payment_status: Optional[str] = None
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    psychologist: PsychologistListItem
    user: UserResponse
    
    class Config:
        from_attributes = True


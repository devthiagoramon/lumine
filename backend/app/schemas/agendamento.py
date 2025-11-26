"""
Appointment Schemas
"""
from pydantic import BaseModel, Field
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
    psychologist_id: int = Field(alias="id_psicologo", serialization_alias="psychologist_id")
    user_id: int = Field(alias="id_usuario", serialization_alias="user_id")
    appointment_date: datetime = Field(alias="data_agendamento", serialization_alias="appointment_date")
    appointment_type: str = Field(alias="tipo_agendamento", serialization_alias="appointment_type")
    status: str
    rejection_reason: Optional[str] = Field(default=None, alias="motivo_recusa", serialization_alias="rejection_reason")
    notes: Optional[str] = Field(default=None, alias="observacoes", serialization_alias="notes")
    payment_status: Optional[str] = Field(default=None, alias="status_pagamento", serialization_alias="payment_status")
    payment_id: Optional[str] = Field(default=None, alias="id_pagamento", serialization_alias="payment_id")
    created_at: datetime = Field(alias="criado_em", serialization_alias="created_at")
    updated_at: Optional[datetime] = Field(default=None, alias="atualizado_em", serialization_alias="updated_at")
    psychologist: PsychologistListItem
    user: UserResponse
    
    class Config:
        from_attributes = True
        populate_by_name = True


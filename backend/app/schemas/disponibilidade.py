"""
Availability Schemas
"""
from pydantic import BaseModel, Field
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
    psychologist_id: int = Field(alias="id_psicologo")
    day_of_week: int = Field(alias="dia_da_semana")
    start_time: str = Field(alias="horario_inicio")
    end_time: str = Field(alias="horario_fim")
    is_available: bool = Field(alias="esta_disponivel")
    created_at: datetime = Field(alias="criado_em")
    updated_at: Optional[datetime] = Field(default=None, alias="atualizado_em")
    
    class Config:
        from_attributes = True
        populate_by_name = True


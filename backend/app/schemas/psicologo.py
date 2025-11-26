"""
Psychologist Schemas
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.autenticacao import UserResponse
from app.schemas.especialidade import SpecialtyResponse
from app.schemas.abordagem import ApproachResponse

class PsychologistBase(BaseModel):
    crp: str
    bio: Optional[str] = Field(default=None, alias="biografia")
    experience_years: int = Field(default=0, alias="anos_experiencia")
    consultation_price: Optional[float] = Field(default=None, alias="preco_consulta")
    online_consultation: bool = Field(default=True, alias="consulta_online")
    in_person_consultation: bool = Field(default=False, alias="consulta_presencial")
    address: Optional[str] = Field(default=None, alias="endereco")
    city: Optional[str] = Field(default=None, alias="cidade")
    state: Optional[str] = Field(default=None, alias="estado")
    zip_code: Optional[str] = Field(default=None, alias="cep")
    profile_picture: Optional[str] = Field(default=None, alias="foto_perfil")
    
    class Config:
        populate_by_name = True

class PsychologistCreate(BaseModel):
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
    user_id: int = Field(alias="id_usuario")
    rating: float = Field(alias="avaliacao")
    total_reviews: int = Field(alias="total_avaliacoes")
    is_verified: bool = Field(alias="esta_verificado")
    created_at: datetime = Field(alias="criado_em")
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    user: UserResponse
    
    class Config:
        from_attributes = True
        populate_by_name = True

class PsychologistListItem(BaseModel):
    id: int
    user_id: int = Field(alias="id_usuario")
    crp: str
    bio: Optional[str] = Field(default=None, alias="biografia")
    experience_years: int = Field(default=0, alias="anos_experiencia")
    consultation_price: Optional[float] = Field(default=None, alias="preco_consulta")
    online_consultation: bool = Field(default=True, alias="consulta_online")
    in_person_consultation: bool = Field(default=False, alias="consulta_presencial")
    city: Optional[str] = Field(default=None, alias="cidade")
    state: Optional[str] = Field(default=None, alias="estado")
    profile_picture: Optional[str] = Field(default=None, alias="foto_perfil")
    rating: float = Field(default=0.0, alias="avaliacao")
    total_reviews: int = Field(default=0, alias="total_avaliacoes")
    is_verified: bool = Field(default=False, alias="esta_verificado")
    user: UserResponse
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    
    class Config:
        from_attributes = True
        populate_by_name = True


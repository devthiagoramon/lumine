"""
Auth Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    is_psychologist: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    nome_completo: str
    telefone: Optional[str] = None
    esta_ativo: bool = Field(alias="esta_ativo")
    eh_psicologo: bool = Field(alias="eh_psicologo")
    eh_admin: bool = Field(alias="eh_admin")
    criado_em: datetime = Field(alias="criado_em")
    
    class Config:
        from_attributes = True
        populate_by_name = True


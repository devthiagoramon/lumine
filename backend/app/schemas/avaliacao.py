"""
Review Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.autenticacao import UserResponse

class ReviewCreate(BaseModel):
    psychologist_id: int
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    psychologist_id: int = Field(alias="id_psicologo", serialization_alias="psychologist_id")
    user_id: int = Field(alias="id_usuario", serialization_alias="user_id")
    rating: int = Field(alias="avaliacao", serialization_alias="rating")
    comment: Optional[str] = Field(default=None, alias="comentario", serialization_alias="comment")
    created_at: datetime = Field(alias="criado_em", serialization_alias="created_at")
    user: UserResponse
    
    class Config:
        from_attributes = True
        populate_by_name = True


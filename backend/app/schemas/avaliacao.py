"""
Review Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.autenticacao import UserResponse

class ReviewCreate(BaseModel):
    psychologist_id: int
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    psychologist_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True


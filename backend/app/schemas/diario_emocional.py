"""
Emotion Diary Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EmotionDiaryCreate(BaseModel):
    date: datetime
    emotion: str
    intensity: int  # 1-10
    notes: Optional[str] = None
    tags: Optional[str] = None

class EmotionDiaryUpdate(BaseModel):
    date: Optional[datetime] = None
    emotion: Optional[str] = None
    intensity: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

class EmotionDiaryResponse(BaseModel):
    id: int
    user_id: int = Field(alias="id_usuario", serialization_alias="user_id")
    date: datetime = Field(alias="data", serialization_alias="date")
    emotion: str = Field(alias="emocao", serialization_alias="emotion")
    intensity: int = Field(alias="intensidade", serialization_alias="intensity")
    notes: Optional[str] = Field(default=None, alias="notas", serialization_alias="notes")
    tags: Optional[str] = Field(default=None, alias="tags", serialization_alias="tags")
    created_at: datetime = Field(alias="criado_em", serialization_alias="created_at")
    updated_at: Optional[datetime] = Field(default=None, alias="atualizado_em", serialization_alias="updated_at")
    
    class Config:
        from_attributes = True
        populate_by_name = True


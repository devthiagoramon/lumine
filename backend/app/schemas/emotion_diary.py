"""
Emotion Diary Schemas
"""
from pydantic import BaseModel
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
    user_id: int
    date: datetime
    emotion: str
    intensity: int
    notes: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


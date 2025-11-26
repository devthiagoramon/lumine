"""
Forum Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.autenticacao import UserResponse

class ForumPostCreate(BaseModel):
    title: str
    content: str
    category: str = 'geral'
    is_anonymous: bool = False

class ForumPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class ForumPostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    category: str
    is_anonymous: bool
    views: int
    likes: int
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None
    comments_count: int = 0
    
    class Config:
        from_attributes = True

class ForumCommentCreate(BaseModel):
    content: str
    is_anonymous: bool = False

class ForumCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    is_anonymous: bool
    likes: int
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


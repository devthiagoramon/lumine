"""
Forum Schemas
"""
from pydantic import BaseModel, Field
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
    user_id: int = Field(alias="id_usuario", serialization_alias="user_id")
    title: str = Field(alias="titulo", serialization_alias="title")
    content: str = Field(alias="conteudo", serialization_alias="content")
    category: str = Field(alias="categoria", serialization_alias="category")
    is_anonymous: bool = Field(alias="eh_anonimo", serialization_alias="is_anonymous")
    views: int = Field(alias="visualizacoes", serialization_alias="views")
    likes: int = Field(alias="curtidas", serialization_alias="likes")
    created_at: datetime = Field(alias="criado_em", serialization_alias="created_at")
    updated_at: Optional[datetime] = Field(default=None, alias="atualizado_em", serialization_alias="updated_at")
    user: Optional[UserResponse] = None
    comments_count: int = 0
    
    class Config:
        from_attributes = True
        populate_by_name = True

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


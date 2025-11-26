"""
Approach Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional

class ApproachBase(BaseModel):
    name: str = Field(alias="nome")
    description: Optional[str] = Field(default=None, alias="descricao")
    
    class Config:
        populate_by_name = True

class ApproachResponse(ApproachBase):
    id: int
    
    class Config:
        from_attributes = True
        populate_by_name = True


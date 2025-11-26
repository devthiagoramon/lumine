"""
Approach Schemas
"""
from pydantic import BaseModel
from typing import Optional

class ApproachBase(BaseModel):
    name: str
    description: Optional[str] = None

class ApproachResponse(ApproachBase):
    id: int
    
    class Config:
        from_attributes = True


"""
Specialty Schemas
"""
from pydantic import BaseModel
from typing import Optional

class SpecialtyBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpecialtyResponse(SpecialtyBase):
    id: int
    
    class Config:
        from_attributes = True


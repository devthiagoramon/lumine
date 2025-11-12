"""
Favorite Schemas
"""
from pydantic import BaseModel
from app.schemas.psychologist import PsychologistListItem

class FavoriteResponse(BaseModel):
    psychologist: PsychologistListItem
    
    class Config:
        from_attributes = True


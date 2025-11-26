"""
Search Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.psicologo import PsychologistListItem

class SearchFilters(BaseModel):
    query: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    specialty_ids: Optional[List[int]] = None
    approach_ids: Optional[List[int]] = None
    online_consultation: Optional[bool] = None
    in_person_consultation: Optional[bool] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    min_experience: Optional[int] = None

class SearchResponse(BaseModel):
    psychologists: List[PsychologistListItem]
    total: int
    page: int
    page_size: int


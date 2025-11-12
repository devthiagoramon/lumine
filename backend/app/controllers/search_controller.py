"""
Search Controller - Endpoints de busca
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import SearchResponse, SpecialtyResponse, ApproachResponse
from app.models.specialty import Specialty
from app.models.approach import Approach
from app.services.search_service import SearchService

router = APIRouter()

@router.get("/psychologists", response_model=SearchResponse)
def search_psychologists(
    query: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    specialty_ids: Optional[List[int]] = Query(None),
    approach_ids: Optional[List[int]] = Query(None),
    online_consultation: Optional[bool] = Query(None),
    in_person_consultation: Optional[bool] = Query(None),
    min_rating: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_experience: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Buscar psicólogos com filtros"""
    result = SearchService.search_psychologists(
        db=db,
        query=query,
        city=city,
        state=state,
        specialty_ids=specialty_ids,
        approach_ids=approach_ids,
        online_consultation=online_consultation,
        in_person_consultation=in_person_consultation,
        min_rating=min_rating,
        max_price=max_price,
        min_experience=min_experience,
        page=page,
        page_size=page_size
    )
    return result

@router.get("/specialties", response_model=List[SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    """Listar especialidades"""
    specialties = db.query(Specialty).all()
    return specialties

@router.get("/approaches", response_model=List[ApproachResponse])
def get_approaches(db: Session = Depends(get_db)):
    """Listar abordagens"""
    approaches = db.query(Approach).all()
    return approaches


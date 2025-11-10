from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from app.database import get_db
from app import schemas, models

router = APIRouter()

@router.get("/psychologists", response_model=schemas.SearchResponse)
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
    # Query base
    q = db.query(models.Psychologist)
    
    # Filtro por busca textual (nome, bio, CRP)
    if query:
        search_term = f"%{query}%"
        q = q.join(models.User).filter(
            or_(
                models.User.full_name.ilike(search_term),
                models.Psychologist.bio.ilike(search_term),
                models.Psychologist.crp.ilike(search_term)
            )
        )
    
    # Filtro por cidade
    if city:
        q = q.filter(models.Psychologist.city.ilike(f"%{city}%"))
    
    # Filtro por estado
    if state:
        q = q.filter(models.Psychologist.state.ilike(f"%{state}%"))
    
    # Filtro por especialidades
    if specialty_ids:
        q = q.join(models.Psychologist.specialties).filter(
            models.Specialty.id.in_(specialty_ids)
        )
    
    # Filtro por abordagens
    if approach_ids:
        q = q.join(models.Psychologist.approaches).filter(
            models.Approach.id.in_(approach_ids)
        )
    
    # Aplicar distinct se houver joins
    if specialty_ids or approach_ids:
        q = q.distinct()
    
    # Filtro por tipo de consulta
    if online_consultation is not None:
        q = q.filter(models.Psychologist.online_consultation == online_consultation)
    
    if in_person_consultation is not None:
        q = q.filter(models.Psychologist.in_person_consultation == in_person_consultation)
    
    # Filtro por rating mínimo
    if min_rating is not None:
        q = q.filter(models.Psychologist.rating >= min_rating)
    
    # Filtro por preço máximo
    if max_price is not None:
        q = q.filter(
            or_(
                models.Psychologist.consultation_price <= max_price,
                models.Psychologist.consultation_price.is_(None)
            )
        )
    
    # Filtro por experiência mínima
    if min_experience is not None:
        q = q.filter(models.Psychologist.experience_years >= min_experience)
    
    # Contar total
    total = q.count()
    
    # Paginação
    skip = (page - 1) * page_size
    psychologists = q.options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).order_by(
        models.Psychologist.rating.desc(),
        models.Psychologist.total_reviews.desc()
    ).offset(skip).limit(page_size).all()
    
    return {
        "psychologists": psychologists,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/specialties", response_model=List[schemas.SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    specialties = db.query(models.Specialty).all()
    return specialties

@router.get("/approaches", response_model=List[schemas.ApproachResponse])
def get_approaches(db: Session = Depends(get_db)):
    approaches = db.query(models.Approach).all()
    return approaches


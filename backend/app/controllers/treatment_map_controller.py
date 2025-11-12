"""
Treatment Map Controller - Endpoints de mapa interativo
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.schemas.psychologist import PsychologistListItem
from app.models.psychologist import Psychologist
from app.models.specialty import Specialty
from app.models.approach import Approach
from pydantic import BaseModel

router = APIRouter()

class TreatmentMapPoint(BaseModel):
    psychologist_id: int
    name: str
    city: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    specialty: str
    approach: str
    rating: float
    price: Optional[float] = None

class TreatmentMapResponse(BaseModel):
    points: List[TreatmentMapPoint]
    total: int

@router.get("/", response_model=TreatmentMapResponse)
def get_treatment_map(
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    specialty_id: Optional[int] = Query(None),
    approach_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obter mapa interativo de tratamentos"""
    query = db.query(Psychologist).options(
        joinedload(Psychologist.user),
        joinedload(Psychologist.specialties),
        joinedload(Psychologist.approaches)
    ).filter(
        Psychologist.is_verified == True
    )
    
    # Filtros
    if city:
        query = query.filter(Psychologist.city.ilike(f"%{city}%"))
    
    if state:
        query = query.filter(Psychologist.state.ilike(f"%{state}%"))
    
    if specialty_id:
        query = query.join(Psychologist.specialties).filter(
            Specialty.id == specialty_id
        )
    
    if approach_id:
        query = query.join(Psychologist.approaches).filter(
            Approach.id == approach_id
        )
    
    psychologists = query.all()
    
    points = []
    for psych in psychologists:
        # Pegar primeira especialidade e abordagem para exibição
        specialty = psych.specialties[0].name if psych.specialties else "Geral"
        approach = psych.approaches[0].name if psych.approaches else "Integrativa"
        
        points.append(TreatmentMapPoint(
            psychologist_id=psych.id,
            name=psych.user.full_name,
            city=psych.city or "",
            state=psych.state or "",
            specialty=specialty,
            approach=approach,
            rating=psych.rating or 0.0,
            price=psych.consultation_price
        ))
    
    return TreatmentMapResponse(
        points=points,
        total=len(points)
    )


"""
Treatment Map Controller - Endpoints de mapa interativo
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from app.schemas.psychologist import PsychologistListItem
from app.models.psychologist import Psychologist
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
def obter_mapa_tratamento(
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    id_especialidade: Optional[int] = Query(None),
    id_abordagem: Optional[int] = Query(None)
):
    """Obter mapa interativo de tratamentos"""
    psychologists = Psychologist.buscar_para_mapa(
        cidade=cidade,
        estado=estado,
        id_especialidade=id_especialidade,
        id_abordagem=id_abordagem
    )
    
    points = []
    for psych in psychologists:
        # Pegar primeira especialidade e abordagem para exibição
        specialty = psych.specialties[0].name if psych.specialties else "Geral"
        approach = psych.approaches[0].name if psych.approaches else "Integrativa"
        
        points.append(TreatmentMapPoint(
            psychologist_id=psych.id,
            name=psych.user.nome_completo,
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


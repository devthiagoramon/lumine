"""
Availability Controller - Endpoints de disponibilidade
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistAvailabilityCreate, PsychologistAvailabilityUpdate,
    PsychologistAvailabilityResponse
)
from app.models.user import User
from app.models.psychologist import Psychologist
from app.services.availability_service import AvailabilityService

router = APIRouter()

@router.post("/", response_model=PsychologistAvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability: PsychologistAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar horário de disponibilidade"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create availability"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Validar dia da semana
    if availability.day_of_week < 0 or availability.day_of_week > 6:
        raise HTTPException(
            status_code=400,
            detail="day_of_week must be between 0 (Monday) and 6 (Sunday)"
        )
    
    # Verificar se já existe disponibilidade para este dia
    existing = AvailabilityService.get_availability_by_id(
        db=db,
        availability_id=0,  # Não usado aqui, vamos verificar manualmente
        psychologist_id=psychologist.id
    )
    
    # Verificar duplicatas de forma diferente
    from app.models.psychologist_availability import PsychologistAvailability
    existing_availability = db.query(PsychologistAvailability).filter(
        PsychologistAvailability.psychologist_id == psychologist.id,
        PsychologistAvailability.day_of_week == availability.day_of_week
    ).first()
    
    if existing_availability:
        raise HTTPException(
            status_code=400,
            detail="Availability for this day already exists. Use update instead."
        )
    
    availability_data = availability.dict()
    db_availability = AvailabilityService.create_availability(
        db=db,
        psychologist_id=psychologist.id,
        availability_data=availability_data
    )
    
    return db_availability

@router.get("/", response_model=List[PsychologistAvailabilityResponse])
def get_my_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter horários de disponibilidade do psicólogo logado"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view availability"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    availability = AvailabilityService.get_availability_by_psychologist(
        db=db,
        psychologist_id=psychologist.id,
        only_available=False
    )
    
    return availability

@router.get("/psychologist/{psychologist_id}", response_model=List[PsychologistAvailabilityResponse])
def get_psychologist_availability(
    psychologist_id: int,
    db: Session = Depends(get_db)
):
    """Obter horários de disponibilidade de um psicólogo"""
    psychologist = db.query(Psychologist).filter(
        Psychologist.id == psychologist_id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    availability = AvailabilityService.get_availability_by_psychologist(
        db=db,
        psychologist_id=psychologist_id,
        only_available=True
    )
    
    return availability

@router.put("/{availability_id}", response_model=PsychologistAvailabilityResponse)
def update_availability(
    availability_id: int,
    availability_update: PsychologistAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Atualizar horário de disponibilidade"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can update availability"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    availability = AvailabilityService.get_availability_by_id(
        db=db,
        availability_id=availability_id,
        psychologist_id=psychologist.id
    )
    
    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability not found"
        )
    
    update_data = availability_update.dict(exclude_unset=True)
    db_availability = AvailabilityService.update_availability(
        db=db,
        availability=availability,
        update_data=update_data
    )
    
    return db_availability

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Deletar horário de disponibilidade"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can delete availability"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    success = AvailabilityService.delete_availability(
        db=db,
        availability_id=availability_id,
        psychologist_id=psychologist.id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Availability not found"
        )
    
    return None


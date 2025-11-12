"""
Pre Registration Controller - Endpoints de pré-cadastro
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistPreRegistrationCreate, PsychologistPreRegistrationResponse
)
from app.models.user import User
from app.models.psychologist_pre_registration import PsychologistPreRegistration
from app.services.pre_registration_service import PreRegistrationService

router = APIRouter()

@router.post("/", response_model=PsychologistPreRegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_pre_registration(
    pre_registration: PsychologistPreRegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar pré-cadastro de psicólogo"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create pre-registration"
        )
    
    # Verificar se já tem pré-cadastro pendente
    existing = PreRegistrationService.get_pre_registration_by_user_id(
        db=db,
        user_id=current_user.id
    )
    
    if existing and existing.status == 'pending':
        raise HTTPException(
            status_code=400,
            detail="You already have a pending pre-registration"
        )
    
    # Verificar se CRP já existe
    existing_crp = db.query(PsychologistPreRegistration).filter(
        PsychologistPreRegistration.crp == pre_registration.crp
    ).first()
    
    if existing_crp:
        raise HTTPException(
            status_code=400,
            detail="CRP already registered"
        )
    
    # Criar pré-cadastro usando service
    pre_registration_data = pre_registration.dict(exclude={"specialty_ids", "approach_ids"})
    db_pre_registration = PreRegistrationService.create_pre_registration(
        db=db,
        user_id=current_user.id,
        pre_registration_data=pre_registration_data,
        specialty_ids=pre_registration.specialty_ids,
        approach_ids=pre_registration.approach_ids
    )
    
    return db_pre_registration

@router.get("/my-pre-registration", response_model=PsychologistPreRegistrationResponse)
def get_my_pre_registration(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meu pré-cadastro"""
    pre_registration = PreRegistrationService.get_pre_registration_by_user_id(
        db=db,
        user_id=current_user.id
    )
    
    if not pre_registration:
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found"
        )
    
    return pre_registration


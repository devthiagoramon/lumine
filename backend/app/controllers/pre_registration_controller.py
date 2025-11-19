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
import json

router = APIRouter()

@router.post("/", response_model=PsychologistPreRegistrationResponse, status_code=status.HTTP_201_CREATED)
def criar_pre_cadastro(
    pre_cadastro: PsychologistPreRegistrationCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar pré-cadastro de psicólogo"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create pre-registration"
        )
    
    # Verificar se já tem pré-cadastro pendente
    existing = PsychologistPreRegistration.verificar_pendente(db, usuario_atual.id)
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending pre-registration"
        )
    
    # Verificar se CRP já existe
    existing_crp = PsychologistPreRegistration.verificar_crp_existente(db, pre_cadastro.crp)
    
    if existing_crp:
        raise HTTPException(
            status_code=400,
            detail="CRP already registered"
        )
    
    # Criar pré-cadastro
    pre_registration_data = pre_cadastro.dict(exclude={"specialty_ids", "approach_ids"})
    db_pre_registration = PsychologistPreRegistration.criar(
        db,
        user_id=usuario_atual.id,
        specialty_ids=json.dumps(pre_cadastro.specialty_ids) if pre_cadastro.specialty_ids else "[]",
        approach_ids=json.dumps(pre_cadastro.approach_ids) if pre_cadastro.approach_ids else "[]",
        **pre_registration_data
    )
    
    return db_pre_registration

@router.get("/my-pre-registration", response_model=PsychologistPreRegistrationResponse)
def obter_meu_pre_cadastro(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meu pré-cadastro"""
    pre_registration = PsychologistPreRegistration.obter_por_usuario(db, usuario_atual.id)
    
    if not pre_registration:
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found"
        )
    
    return pre_registration


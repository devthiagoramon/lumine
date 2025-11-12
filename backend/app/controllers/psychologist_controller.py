"""
Psychologist Controller - Endpoints de psicólogos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistCreate, PsychologistUpdate, PsychologistResponse, PsychologistListItem
)
from app.models.user import User
from app.models.psychologist import Psychologist
from app.services.psychologist_service import PsychologistService

router = APIRouter()

@router.post("/", response_model=PsychologistResponse, status_code=status.HTTP_201_CREATED)
def create_psychologist_profile(
    psychologist: PsychologistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar perfil de psicólogo"""
    # Verificar se usuário é psicólogo
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create profiles"
        )
    
    # Verificar se já tem perfil
    existing = PsychologistService.get_psychologist_by_user_id(db, current_user.id, load_relationships=False)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Psychologist profile already exists"
        )
    
    # Verificar se CRP já existe
    existing_crp = db.query(Psychologist).filter(
        Psychologist.crp == psychologist.crp
    ).first()
    if existing_crp:
        raise HTTPException(
            status_code=400,
            detail="CRP already registered"
        )
    
    # Criar perfil
    psychologist_data = psychologist.dict(exclude={"specialty_ids", "approach_ids"})
    db_psychologist = PsychologistService.create_psychologist(
        db=db,
        user_id=current_user.id,
        psychologist_data=psychologist_data,
        specialty_ids=psychologist.specialty_ids,
        approach_ids=psychologist.approach_ids
    )
    
    # Recarregar com relacionamentos
    db_psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=db_psychologist.id,
        load_relationships=True
    )
    
    return db_psychologist

@router.get("/me", response_model=PsychologistResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meu perfil de psicólogo"""
    psychologist = PsychologistService.get_psychologist_by_user_id(
        db=db,
        user_id=current_user.id,
        load_relationships=True
    )
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    return psychologist

@router.put("/me", response_model=PsychologistResponse)
def update_my_profile(
    psychologist_update: PsychologistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Atualizar meu perfil de psicólogo"""
    psychologist = PsychologistService.get_psychologist_by_user_id(
        db=db,
        user_id=current_user.id,
        load_relationships=False
    )
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Atualizar campos
    update_data = psychologist_update.dict(exclude_unset=True, exclude={"specialty_ids", "approach_ids"})
    db_psychologist = PsychologistService.update_psychologist(
        db=db,
        psychologist=psychologist,
        update_data=update_data,
        specialty_ids=psychologist_update.specialty_ids,
        approach_ids=psychologist_update.approach_ids
    )
    
    # Recarregar com relacionamentos
    db_psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=db_psychologist.id,
        load_relationships=True
    )
    
    return db_psychologist

@router.get("/{psychologist_id}", response_model=PsychologistResponse)
def get_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db)
):
    """Obter psicólogo por ID"""
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist_id,
        load_relationships=True
    )
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    return psychologist

@router.get("/", response_model=List[PsychologistListItem])
def list_psychologists(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Listar psicólogos"""
    psychologists = PsychologistService.list_psychologists(
        db=db,
        skip=skip,
        limit=limit,
        load_relationships=True
    )
    return psychologists


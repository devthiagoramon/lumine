from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import auth, schemas, models

router = APIRouter()

@router.post("/", response_model=schemas.PsychologistResponse, status_code=status.HTTP_201_CREATED)
def create_psychologist_profile(
    psychologist: schemas.PsychologistCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se usuário é psicólogo
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create profiles"
        )
    
    # Verificar se já tem perfil
    existing = db.query(models.Psychologist).filter(
        models.Psychologist.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Psychologist profile already exists"
        )
    
    # Verificar se CRP já existe
    existing_crp = db.query(models.Psychologist).filter(
        models.Psychologist.crp == psychologist.crp
    ).first()
    if existing_crp:
        raise HTTPException(
            status_code=400,
            detail="CRP already registered"
        )
    
    # Criar perfil
    db_psychologist = models.Psychologist(
        user_id=current_user.id,
        **psychologist.dict(exclude={"specialty_ids", "approach_ids"})
    )
    
    # Adicionar especialidades
    if psychologist.specialty_ids:
        specialties = db.query(models.Specialty).filter(
            models.Specialty.id.in_(psychologist.specialty_ids)
        ).all()
        db_psychologist.specialties = specialties
    
    # Adicionar abordagens
    if psychologist.approach_ids:
        approaches = db.query(models.Approach).filter(
            models.Approach.id.in_(psychologist.approach_ids)
        ).all()
        db_psychologist.approaches = approaches
    
    db.add(db_psychologist)
    db.commit()
    db.refresh(db_psychologist)
    # Recarregar com relacionamentos
    db_psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(models.Psychologist.id == db_psychologist.id).first()
    return db_psychologist

@router.get("/me", response_model=schemas.PsychologistResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(
        models.Psychologist.user_id == current_user.id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    return psychologist

@router.put("/me", response_model=schemas.PsychologistResponse)
def update_my_profile(
    psychologist_update: schemas.PsychologistUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.user_id == current_user.id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Atualizar campos
    update_data = psychologist_update.dict(exclude_unset=True, exclude={"specialty_ids", "approach_ids"})
    for field, value in update_data.items():
        setattr(psychologist, field, value)
    
    # Atualizar especialidades
    if psychologist_update.specialty_ids is not None:
        specialties = db.query(models.Specialty).filter(
            models.Specialty.id.in_(psychologist_update.specialty_ids)
        ).all()
        psychologist.specialties = specialties
    
    # Atualizar abordagens
    if psychologist_update.approach_ids is not None:
        approaches = db.query(models.Approach).filter(
            models.Approach.id.in_(psychologist_update.approach_ids)
        ).all()
        psychologist.approaches = approaches
    
    db.commit()
    db.refresh(psychologist)
    # Recarregar com relacionamentos
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(models.Psychologist.id == psychologist.id).first()
    return psychologist

@router.get("/{psychologist_id}", response_model=schemas.PsychologistResponse)
def get_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db)
):
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    return psychologist

@router.get("/", response_model=List[schemas.PsychologistListItem])
def list_psychologists(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    psychologists = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).offset(skip).limit(limit).all()
    return psychologists


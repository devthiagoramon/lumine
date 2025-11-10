from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import auth, schemas, models

router = APIRouter()

@router.post("/{psychologist_id}", status_code=status.HTTP_201_CREATED)
def add_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se psicólogo existe
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Verificar se já está nos favoritos
    if psychologist in current_user.favorite_psychologists:
        raise HTTPException(
            status_code=400,
            detail="Psychologist already in favorites"
        )
    
    # Adicionar aos favoritos
    current_user.favorite_psychologists.append(psychologist)
    db.commit()
    
    return {"message": "Psychologist added to favorites"}

@router.delete("/{psychologist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se psicólogo existe
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Remover dos favoritos
    if psychologist in current_user.favorite_psychologists:
        current_user.favorite_psychologists.remove(psychologist)
        db.commit()
    
    return None

@router.get("/", response_model=List[schemas.PsychologistListItem])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Recarregar usuário com favoritos
    user = db.query(models.User).options(
        joinedload(models.User.favorite_psychologists).joinedload(models.Psychologist.user),
        joinedload(models.User.favorite_psychologists).joinedload(models.Psychologist.specialties),
        joinedload(models.User.favorite_psychologists).joinedload(models.Psychologist.approaches)
    ).filter(models.User.id == current_user.id).first()
    
    return user.favorite_psychologists

@router.get("/check/{psychologist_id}")
def check_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se psicólogo existe
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Recarregar usuário com favoritos
    user = db.query(models.User).options(
        joinedload(models.User.favorite_psychologists)
    ).filter(models.User.id == current_user.id).first()
    
    is_favorite = psychologist in user.favorite_psychologists
    
    return {"is_favorite": is_favorite}


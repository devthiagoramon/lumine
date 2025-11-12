"""
Favorite Controller - Endpoints de favoritos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import PsychologistListItem
from app.models.user import User
from app.services.favorite_service import FavoriteService

router = APIRouter()

@router.post("/{psychologist_id}", status_code=status.HTTP_201_CREATED)
def add_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Adicionar psicólogo aos favoritos"""
    success = FavoriteService.add_favorite(
        db=db,
        user_id=current_user.id,
        psychologist_id=psychologist_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Psychologist not found or already in favorites"
        )
    
    return {"message": "Psychologist added to favorites"}

@router.delete("/{psychologist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Remover psicólogo dos favoritos"""
    success = FavoriteService.remove_favorite(
        db=db,
        user_id=current_user.id,
        psychologist_id=psychologist_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found in favorites"
        )
    
    return None

@router.get("/", response_model=List[PsychologistListItem])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter favoritos"""
    favorites = FavoriteService.get_favorites(
        db=db,
        user_id=current_user.id
    )
    return favorites

@router.get("/check/{psychologist_id}")
def check_favorite(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Verificar se psicólogo está nos favoritos"""
    is_favorite = FavoriteService.is_favorite(
        db=db,
        user_id=current_user.id,
        psychologist_id=psychologist_id
    )
    
    return {"is_favorite": is_favorite}


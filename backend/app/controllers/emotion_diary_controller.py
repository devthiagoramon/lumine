"""
Emotion Diary Controller - Endpoints de diário de emoções
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import auth
from app.schemas import (
    EmotionDiaryCreate, EmotionDiaryUpdate, EmotionDiaryResponse
)
from app.models.user import User
from app.models.emotion_diary import EmotionDiary
from app.services.emotion_diary_service import EmotionDiaryService

router = APIRouter()

@router.post("/", response_model=EmotionDiaryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: EmotionDiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar entrada no diário"""
    # Validar intensidade
    if entry.intensity < 1 or entry.intensity > 10:
        raise HTTPException(
            status_code=400,
            detail="Intensity must be between 1 and 10"
        )
    
    entry_data = entry.dict()
    db_entry = EmotionDiaryService.create_entry(
        db=db,
        user_id=current_user.id,
        entry_data=entry_data
    )
    
    return db_entry

@router.get("/", response_model=List[EmotionDiaryResponse])
def get_entries(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    emotion: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter entradas do diário"""
    entries = EmotionDiaryService.get_entries(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        emotion=emotion
    )
    return entries

@router.get("/stats")
def get_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter estatísticas do diário"""
    stats = EmotionDiaryService.get_stats(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return stats

@router.get("/{entry_id}", response_model=EmotionDiaryResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter entrada por ID"""
    entry = EmotionDiaryService.get_entry_by_id(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id
    )
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    return entry

@router.put("/{entry_id}", response_model=EmotionDiaryResponse)
def update_entry(
    entry_id: int,
    entry_update: EmotionDiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Atualizar entrada"""
    entry = EmotionDiaryService.get_entry_by_id(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id
    )
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    # Validar intensidade se fornecida
    if entry_update.intensity is not None:
        if entry_update.intensity < 1 or entry_update.intensity > 10:
            raise HTTPException(
                status_code=400,
                detail="Intensity must be between 1 and 10"
            )
    
    update_data = entry_update.dict(exclude_unset=True)
    db_entry = EmotionDiaryService.update_entry(
        db=db,
        entry=entry,
        update_data=update_data
    )
    
    return db_entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Deletar entrada"""
    success = EmotionDiaryService.delete_entry(
        db=db,
        entry_id=entry_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    return None

@router.get("/emotions/list")
def get_emotions_list():
    """Obter lista de emoções"""
    return {
        "emotions": [
            {"value": "feliz", "label": "Feliz"},
            {"value": "triste", "label": "Triste"},
            {"value": "ansioso", "label": "Ansioso"},
            {"value": "irritado", "label": "Irritado"},
            {"value": "calmo", "label": "Calmo"},
            {"value": "estressado", "label": "Estressado"},
            {"value": "motivado", "label": "Motivado"},
            {"value": "cansado", "label": "Cansado"},
            {"value": "gratidão", "label": "Gratidão"},
            {"value": "medo", "label": "Medo"},
            {"value": "raiva", "label": "Raiva"},
            {"value": "esperança", "label": "Esperança"},
            {"value": "confuso", "label": "Confuso"},
            {"value": "orgulhoso", "label": "Orgulhoso"},
            {"value": "culpado", "label": "Culpado"}
        ]
    }


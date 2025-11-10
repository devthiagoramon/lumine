from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app import auth, schemas, models
from sqlalchemy import func, and_, extract

router = APIRouter()

@router.post("/", response_model=schemas.EmotionDiaryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: schemas.EmotionDiaryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Validar intensidade
    if entry.intensity < 1 or entry.intensity > 10:
        raise HTTPException(
            status_code=400,
            detail="Intensity must be between 1 and 10"
        )
    
    db_entry = models.EmotionDiary(
        user_id=current_user.id,
        **entry.dict()
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@router.get("/", response_model=List[schemas.EmotionDiaryResponse])
def get_entries(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    emotion: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.EmotionDiary).filter(
        models.EmotionDiary.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(models.EmotionDiary.date >= start_date)
    
    if end_date:
        query = query.filter(models.EmotionDiary.date <= end_date)
    
    if emotion:
        query = query.filter(models.EmotionDiary.emotion == emotion)
    
    entries = query.order_by(models.EmotionDiary.date.desc()).all()
    
    return entries

@router.get("/stats")
def get_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.EmotionDiary).filter(
        models.EmotionDiary.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(models.EmotionDiary.date >= start_date)
    
    if end_date:
        query = query.filter(models.EmotionDiary.date <= end_date)
    
    # Estatísticas por emoção
    emotion_stats = db.query(
        models.EmotionDiary.emotion,
        func.count(models.EmotionDiary.id).label('count'),
        func.avg(models.EmotionDiary.intensity).label('avg_intensity')
    ).filter(
        models.EmotionDiary.user_id == current_user.id
    )
    
    if start_date:
        emotion_stats = emotion_stats.filter(models.EmotionDiary.date >= start_date)
    
    if end_date:
        emotion_stats = emotion_stats.filter(models.EmotionDiary.date <= end_date)
    
    emotion_stats = emotion_stats.group_by(models.EmotionDiary.emotion).all()
    
    # Média geral de intensidade
    avg_intensity = db.query(func.avg(models.EmotionDiary.intensity)).filter(
        models.EmotionDiary.user_id == current_user.id
    )
    
    if start_date:
        avg_intensity = avg_intensity.filter(models.EmotionDiary.date >= start_date)
    
    if end_date:
        avg_intensity = avg_intensity.filter(models.EmotionDiary.date <= end_date)
    
    avg_intensity = avg_intensity.scalar()
    
    # Total de entradas
    total_entries = query.count()
    
    return {
        "total_entries": total_entries,
        "average_intensity": float(avg_intensity) if avg_intensity else 0,
        "emotion_stats": [
            {
                "emotion": stat.emotion,
                "count": stat.count,
                "average_intensity": float(stat.avg_intensity) if stat.avg_intensity else 0
            }
            for stat in emotion_stats
        ]
    }

@router.get("/{entry_id}", response_model=schemas.EmotionDiaryResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    entry = db.query(models.EmotionDiary).filter(
        models.EmotionDiary.id == entry_id,
        models.EmotionDiary.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    return entry

@router.put("/{entry_id}", response_model=schemas.EmotionDiaryResponse)
def update_entry(
    entry_id: int,
    entry_update: schemas.EmotionDiaryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    entry = db.query(models.EmotionDiary).filter(
        models.EmotionDiary.id == entry_id,
        models.EmotionDiary.user_id == current_user.id
    ).first()
    
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
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    db.commit()
    db.refresh(entry)
    
    return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    entry = db.query(models.EmotionDiary).filter(
        models.EmotionDiary.id == entry_id,
        models.EmotionDiary.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return None

@router.get("/emotions/list")
def get_emotions_list():
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


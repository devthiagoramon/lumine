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

router = APIRouter()

@router.post("/", response_model=EmotionDiaryResponse, status_code=status.HTTP_201_CREATED)
def criar_entrada(
    entrada: EmotionDiaryCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar entrada no diário"""
    # Validar intensidade
    if entrada.intensity < 1 or entrada.intensity > 10:
        raise HTTPException(
            status_code=400,
            detail="Intensity must be between 1 and 10"
        )
    
    db_entry = EmotionDiary.criar(
        db,
        user_id=usuario_atual.id,
        date=entrada.date,
        emotion=entrada.emotion,
        intensity=entrada.intensity,
        notes=entrada.notes,
        tags=entrada.tags
    )
    return db_entry

@router.get("/", response_model=List[EmotionDiaryResponse])
def obter_entradas(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    emocao: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter entradas do diário"""
    entries = EmotionDiary.listar_por_usuario(
        db, usuario_atual.id, 
        data_inicio=data_inicio, 
        data_fim=data_fim, 
        emocao=emocao
    )
    return entries

@router.get("/stats")
def obter_estatisticas(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter estatísticas do diário"""
    stats = EmotionDiary.obter_estatisticas(db, usuario_atual.id, data_inicio=data_inicio, data_fim=data_fim)
    return stats

@router.get("/{id_entrada}", response_model=EmotionDiaryResponse)
def obter_entrada(
    id_entrada: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter entrada por ID"""
    entry = EmotionDiary.obter_por_id(db, id_entrada, usuario_atual.id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    return entry

@router.put("/{id_entrada}", response_model=EmotionDiaryResponse)
def atualizar_entrada(
    id_entrada: int,
    atualizacao_entrada: EmotionDiaryUpdate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar entrada"""
    entry = EmotionDiary.obter_por_id(db, id_entrada, usuario_atual.id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    # Validar intensidade se fornecida
    if atualizacao_entrada.intensity is not None:
        if atualizacao_entrada.intensity < 1 or atualizacao_entrada.intensity > 10:
            raise HTTPException(
                status_code=400,
                detail="Intensity must be between 1 and 10"
            )
    
    update_data = atualizacao_entrada.dict(exclude_unset=True)
    entry.atualizar(db, **update_data)
    
    return entry

@router.delete("/{id_entrada}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_entrada(
    id_entrada: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar entrada"""
    entry = EmotionDiary.obter_por_id(db, id_entrada, usuario_atual.id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )
    
    entry.deletar(db)
    return None

@router.get("/emotions/list")
def obter_lista_emocoes():
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


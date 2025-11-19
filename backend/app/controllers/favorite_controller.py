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
from app.models.psychologist import Psychologist
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/{id_psicologo}", status_code=status.HTTP_201_CREATED)
def adicionar_favorito(
    id_psicologo: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Adicionar psicólogo aos favoritos"""
    usuario = User.obter_por_id(db, usuario_atual.id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    psicologo = Psychologist.obter_por_id(db, id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos(db)
    
    if psicologo in usuario.favorite_psychologists:
        raise HTTPException(
            status_code=400,
            detail="Psicólogo já está nos favoritos"
        )
    
    usuario.favorite_psychologists.append(psicologo)
    db.commit()
    return {"message": "Psicólogo adicionado aos favoritos"}

@router.delete("/{id_psicologo}", status_code=status.HTTP_204_NO_CONTENT)
def remover_favorito(
    id_psicologo: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Remover psicólogo dos favoritos"""
    usuario = User.obter_por_id(db, usuario_atual.id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    psicologo = Psychologist.obter_por_id(db, id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos(db)
    
    if psicologo not in usuario.favorite_psychologists:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado nos favoritos"
        )
    
    usuario.favorite_psychologists.remove(psicologo)
    db.commit()
    return None

@router.get("/", response_model=List[PsychologistListItem])
def obter_favoritos(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter favoritos"""
    usuario = User.obter_por_id(db, usuario_atual.id)
    if not usuario:
        return []
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos_completo(db)
    
    return usuario.favorite_psychologists if usuario else []

@router.get("/verificar/{id_psicologo}")
def verificar_favorito(
    id_psicologo: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Verificar se psicólogo está nos favoritos"""
    usuario = User.obter_por_id(db, usuario_atual.id)
    psicologo = Psychologist.obter_por_id(db, id_psicologo)
    
    if not usuario or not psicologo:
        return {"is_favorite": False}
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos(db)
    
    eh_favorito = psicologo in usuario.favorite_psychologists if usuario else False
    
    return {"is_favorite": eh_favorito}


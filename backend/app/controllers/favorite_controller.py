"""
Favorite Controller - Endpoints de favoritos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import auth
from app.schemas import PsychologistListItem
from app.models.user import User
from app.models.psychologist import Psychologist
from sqlalchemy.orm import joinedload
from app.database import get_db_session

router = APIRouter()

@router.post("/{id_psicologo}", status_code=status.HTTP_201_CREATED)
def adicionar_favorito(
    id_psicologo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Adicionar psicólogo aos favoritos"""
    from app.database import get_db_session
    
    usuario = User.obter_por_id(usuario_atual.id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Recarregar com relacionamentos e adicionar favorito
    db = get_db_session()
    try:
        usuario_db = db.query(User).options(
            joinedload(User.favorite_psychologists)
        ).filter(User.id == usuario.id).first()
        
        if psicologo in usuario_db.favorite_psychologists:
            raise HTTPException(
                status_code=400,
                detail="Psicólogo já está nos favoritos"
            )
        
        usuario_db.favorite_psychologists.append(psicologo)
        db.commit()
    finally:
        db.close()
    
    return {"message": "Psicólogo adicionado aos favoritos"}

@router.delete("/{id_psicologo}", status_code=status.HTTP_204_NO_CONTENT)
def remover_favorito(
    id_psicologo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Remover psicólogo dos favoritos"""
    from app.database import get_db_session
    from sqlalchemy.orm import joinedload
    
    usuario = User.obter_por_id(usuario_atual.id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Recarregar com relacionamentos e remover favorito
    db = get_db_session()
    try:
        usuario_db = db.query(User).options(
            joinedload(User.favorite_psychologists)
        ).filter(User.id == usuario.id).first()
        
        if psicologo not in usuario_db.favorite_psychologists:
            raise HTTPException(
                status_code=404,
                detail="Psicólogo não encontrado nos favoritos"
            )
        
        usuario_db.favorite_psychologists.remove(psicologo)
        db.commit()
    finally:
        db.close()
    
    return None

@router.get("/", response_model=List[PsychologistListItem])
def obter_favoritos(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter favoritos"""
    usuario = User.obter_por_id(usuario_atual.id)
    if not usuario:
        return []
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos_completo()
    
    return usuario.favorite_psychologists if usuario else []

@router.get("/verificar/{id_psicologo}")
def verificar_favorito(
    id_psicologo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Verificar se psicólogo está nos favoritos"""
    usuario = User.obter_por_id(usuario_atual.id)
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not usuario or not psicologo:
        return {"is_favorite": False}
    
    # Recarregar com relacionamentos
    usuario = usuario.obter_com_favoritos()
    
    eh_favorito = psicologo in usuario.favorite_psychologists if usuario else False
    
    return {"is_favorite": eh_favorito}


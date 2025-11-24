"""
Notification Controller - Endpoints de notificações
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app import auth
from app.schemas import NotificationResponse
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def obter_notificacoes(
    lida: Optional[bool] = Query(None),
    limite: int = Query(50, ge=1, le=100),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter notificações do usuário"""
    notificacoes = Notification.listar_por_usuario(usuario_atual.id, lida=lida, limite=limite)
    return notificacoes

@router.get("/contagem-nao-lidas")
def obter_contagem_nao_lidas(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter contagem de notificações não lidas"""
    contagem = Notification.contar_nao_lidas(usuario_atual.id)
    return {"unread_count": contagem}

@router.put("/{id_notificacao}/ler", response_model=NotificationResponse)
def marcar_notificacao_como_lida(
    id_notificacao: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Marcar notificação como lida"""
    notificacoes = Notification.listar_por_usuario(usuario_atual.id, limite=1000)
    notificacao = next((n for n in notificacoes if n.id == id_notificacao), None)
    
    if not notificacao:
        raise HTTPException(
            status_code=404,
            detail="Notificação não encontrada"
        )
    
    notificacao.marcar_como_lida()
    return notificacao

@router.put("/marcar-todas-lidas")
def marcar_todas_como_lidas(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Marcar todas as notificações como lidas"""
    contagem = Notification.marcar_todas_como_lidas(usuario_atual.id)
    return {"marked_count": contagem}


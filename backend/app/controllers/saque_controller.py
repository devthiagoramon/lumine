"""
Withdrawal Controller - Endpoints de saques
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import auth
from app.schemas import WithdrawalCreate, WithdrawalResponse
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.saque import Withdrawal
from app.models.notificacao import Notification

router = APIRouter()

@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
def criar_saque(
    saque: WithdrawalCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Solicitar saque"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem solicitar saques"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    # Verificar saldo disponível
    saldo = psicologo.saldo or 0.0
    if saque.amount > saldo:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: R$ {saldo:.2f}"
        )
    
    if saque.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Valor do saque deve ser maior que 0"
        )
    
    # Criar solicitação de saque
    saque_created = Withdrawal.criar(
        psychologist_id=psicologo.id,
        amount=saque.amount,
        bank_name=saque.bank_name,
        bank_account=saque.bank_account,
        bank_agency=saque.bank_agency,
        account_type=saque.account_type,
        status='pending'
    )
    
    # Reservar valor (subtrair do saldo)
    psicologo.atualizar(saldo=saldo - saque.amount)
    
    # Criar notificação
    Notification.criar(
        user_id=usuario_atual.id,
        title="Solicitação de Saque Criada",
        message=f"Sua solicitação de saque de R$ {saque.amount:.2f} foi criada e está em análise.",
        type="withdrawal",
        related_id=saque_created.id,
        related_type="withdrawal",
        is_read=False
    )
    
    return saque_created

@router.get("/", response_model=List[WithdrawalResponse])
def obter_meus_saques(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus saques"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar saques"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    saques = Withdrawal.listar_por_psicologo(psicologo.id)
    
    return saques

@router.get("/{id_saque}", response_model=WithdrawalResponse)
def obter_saque(
    id_saque: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter saque específico"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar saques"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    saque = Withdrawal.obter_por_id(id_saque, id_psicologo=psicologo.id)
    
    if not saque:
        raise HTTPException(
            status_code=404,
            detail="Saque não encontrado"
        )
    
    return saque


"""
Withdrawal Controller - Endpoints de saques
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import WithdrawalCreate, WithdrawalResponse
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.withdrawal import Withdrawal
from app.models.notification import Notification

router = APIRouter()

@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
def criar_saque(
    saque: WithdrawalCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Solicitar saque"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can request withdrawals"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Verificar saldo disponível
    balance = psychologist.balance or 0.0
    if saque.amount > balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: R$ {balance:.2f}"
        )
    
    if saque.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal amount must be greater than 0"
        )
    
    # Criar solicitação de saque
    db_withdrawal = Withdrawal.criar(
        db,
        psychologist_id=psychologist.id,
        amount=saque.amount,
        bank_name=saque.bank_name,
        bank_account=saque.bank_account,
        bank_agency=saque.bank_agency,
        account_type=saque.account_type,
        status='pending'
    )
    
    # Reservar valor (subtrair do saldo)
    psychologist.atualizar(db, balance=balance - saque.amount)
    
    # Criar notificação
    Notification.criar(
        db,
        user_id=usuario_atual.id,
        title="Solicitação de Saque Criada",
        message=f"Sua solicitação de saque de R$ {saque.amount:.2f} foi criada e está em análise.",
        type="withdrawal",
        related_id=db_withdrawal.id,
        related_type="withdrawal",
        is_read=False
    )
    
    return db_withdrawal

@router.get("/", response_model=List[WithdrawalResponse])
def obter_meus_saques(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus saques"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view withdrawals"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    withdrawals = Withdrawal.listar_por_psicologo(db, psychologist.id)
    
    return withdrawals

@router.get("/{id_saque}", response_model=WithdrawalResponse)
def obter_saque(
    id_saque: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter saque específico"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view withdrawals"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    withdrawal = Withdrawal.obter_por_id(db, id_saque, psychologist_id=psychologist.id)
    
    if not withdrawal:
        raise HTTPException(
            status_code=404,
            detail="Withdrawal not found"
        )
    
    return withdrawal


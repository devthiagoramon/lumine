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
from app.services.withdrawal_service import WithdrawalService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
def create_withdrawal(
    withdrawal: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Solicitar saque"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can request withdrawals"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Verificar saldo disponível
    balance = psychologist.balance or 0.0
    if withdrawal.amount > balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: R$ {balance:.2f}"
        )
    
    if withdrawal.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal amount must be greater than 0"
        )
    
    # Criar solicitação de saque usando service
    withdrawal_data = withdrawal.dict()
    db_withdrawal = WithdrawalService.create_withdrawal(
        db=db,
        psychologist_id=psychologist.id,
        withdrawal_data=withdrawal_data
    )
    
    if not db_withdrawal:
        raise HTTPException(
            status_code=400,
            detail="Failed to create withdrawal"
        )
    
    # Criar notificação
    NotificationService.create_notification(
        db=db,
        user_id=current_user.id,
        title="Solicitação de Saque Criada",
        message=f"Sua solicitação de saque de R$ {withdrawal.amount:.2f} foi criada e está em análise.",
        type="withdrawal",
        related_id=db_withdrawal.id,
        related_type="withdrawal"
    )
    
    return db_withdrawal

@router.get("/", response_model=List[WithdrawalResponse])
def get_my_withdrawals(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meus saques"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view withdrawals"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    withdrawals = WithdrawalService.get_withdrawals_by_psychologist(
        db=db,
        psychologist_id=psychologist.id
    )
    
    return withdrawals

@router.get("/{withdrawal_id}", response_model=WithdrawalResponse)
def get_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter saque específico"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view withdrawals"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    withdrawal = WithdrawalService.get_withdrawal_by_id(
        db=db,
        withdrawal_id=withdrawal_id,
        psychologist_id=psychologist.id
    )
    
    if not withdrawal:
        raise HTTPException(
            status_code=404,
            detail="Withdrawal not found"
        )
    
    return withdrawal


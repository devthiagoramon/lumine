"""
Payment Controller - Endpoints de pagamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import auth
from app.schemas import PaymentCreate, PaymentResponse
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.services.payment_service import PaymentService

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar pagamento"""
    # Verificar se agendamento existe
    appointment = db.query(Appointment).filter(
        Appointment.id == payment.appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Verificar se agendamento pertence ao usuário
    if appointment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only pay for your own appointments"
        )
    
    # Verificar se já foi pago
    existing_payment = PaymentService.get_payment_by_appointment_id(
        db=db,
        appointment_id=payment.appointment_id
    )
    
    if existing_payment and existing_payment.status == 'paid':
        raise HTTPException(
            status_code=400,
            detail="Appointment already paid"
        )
    
    # Obter valor do psicólogo
    psychologist = db.query(Psychologist).filter(
        Psychologist.id == appointment.psychologist_id
    ).first()
    
    if not psychologist or not psychologist.consultation_price:
        raise HTTPException(
            status_code=400,
            detail="Psychologist consultation price not set"
        )
    
    amount = psychologist.consultation_price
    
    # Processar pagamento mockado
    payment_result = PaymentService.process_mock_payment(payment.payment_method, amount)
    
    # Criar registro de pagamento usando service
    payment_data = {
        "amount": amount,
        "payment_method": payment.payment_method,
        "status": payment_result["status"],
        "payment_id": payment_result["payment_id"],
        "transaction_id": payment_result.get("transaction_id")
    }
    db_payment = PaymentService.create_payment(
        db=db,
        appointment_id=payment.appointment_id,
        user_id=current_user.id,
        payment_data=payment_data
    )
    
    # Atualizar status do agendamento
    appointment.payment_status = payment_result["status"]
    appointment.payment_id = payment_result["payment_id"]
    
    if payment_result["status"] == "paid":
        appointment.status = "confirmed"
        # Processar pagamento e atualizar saldo
        PaymentService.process_payment_success(db=db, payment=db_payment, appointment=appointment)
    else:
        db.commit()
        db.refresh(db_payment)
    
    return db_payment

@router.get("/appointment/{appointment_id}", response_model=PaymentResponse)
def get_payment_by_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter pagamento por appointment_id"""
    payment = PaymentService.get_payment_by_appointment_id(
        db=db,
        appointment_id=appointment_id
    )
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    
    # Verificar permissão
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    if appointment.user_id != current_user.id:
        # Verificar se é psicólogo do agendamento
        psychologist = db.query(Psychologist).filter(
            Psychologist.user_id == current_user.id
        ).first()
        
        if not psychologist or appointment.psychologist_id != psychologist.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view this payment"
            )
    
    return payment

@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meus pagamentos"""
    payments = PaymentService.get_payments_by_user(
        db=db,
        user_id=current_user.id
    )
    return payments

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Reembolsar pagamento"""
    payment = PaymentService.refund_payment(
        db=db,
        payment_id=payment_id,
        user_id=current_user.id
    )
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found or cannot be refunded"
        )
    
    return payment

@router.get("/financial-history", response_model=List[PaymentResponse])
def get_financial_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter histórico financeiro (para psicólogos)"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view financial history"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    payments = PaymentService.get_financial_history(
        db=db,
        psychologist_id=psychologist.id
    )
    
    return payments

@router.get("/balance")
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter saldo disponível (para psicólogos)"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view balance"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    return {
        "balance": psychologist.balance or 0.0,
        "psychologist_id": psychologist.id
    }


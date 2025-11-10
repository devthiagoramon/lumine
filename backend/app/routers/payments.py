from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import uuid
from datetime import datetime
from app.database import get_db
from app import auth, schemas, models

router = APIRouter()

def generate_mock_payment_id():
    """Gera um ID mockado de pagamento"""
    return f"PAY-{uuid.uuid4().hex[:16].upper()}"

def generate_mock_transaction_id():
    """Gera um ID mockado de transação"""
    return f"TXN-{uuid.uuid4().hex[:16].upper()}"

def process_mock_payment(payment_method: str, amount: float) -> dict:
    """
    Simula processamento de pagamento
    Retorna status do pagamento (sempre bem-sucedido para mock)
    """
    # Simular delay de processamento
    import time
    time.sleep(0.5)  # Simular processamento
    
    # Mock: 95% de sucesso, 5% de falha
    import random
    success = random.random() > 0.05
    
    if success:
        return {
            "status": "paid",
            "payment_id": generate_mock_payment_id(),
            "transaction_id": generate_mock_transaction_id(),
            "message": "Pagamento processado com sucesso"
        }
    else:
        return {
            "status": "failed",
            "payment_id": generate_mock_payment_id(),
            "transaction_id": None,
            "message": "Falha no processamento do pagamento. Tente novamente."
        }

@router.post("/", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se agendamento existe
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == payment.appointment_id
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
    existing_payment = db.query(models.Payment).filter(
        models.Payment.appointment_id == payment.appointment_id,
        models.Payment.status == 'paid'
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Appointment already paid"
        )
    
    # Obter valor do psicólogo
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == appointment.psychologist_id
    ).first()
    
    if not psychologist or not psychologist.consultation_price:
        raise HTTPException(
            status_code=400,
            detail="Psychologist consultation price not set"
        )
    
    amount = psychologist.consultation_price
    
    # Processar pagamento mockado
    payment_result = process_mock_payment(payment.payment_method, amount)
    
    # Criar registro de pagamento
    db_payment = models.Payment(
        appointment_id=payment.appointment_id,
        user_id=current_user.id,
        amount=amount,
        payment_method=payment.payment_method,
        status=payment_result["status"],
        payment_id=payment_result["payment_id"],
        transaction_id=payment_result.get("transaction_id")
    )
    db.add(db_payment)
    
    # Atualizar status do agendamento
    appointment.payment_status = payment_result["status"]
    appointment.payment_id = payment_result["payment_id"]
    
    if payment_result["status"] == "paid":
        appointment.status = "confirmed"
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

@router.get("/appointment/{appointment_id}", response_model=schemas.PaymentResponse)
def get_payment_by_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    payment = db.query(models.Payment).filter(
        models.Payment.appointment_id == appointment_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    
    # Verificar permissão
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    if appointment.user_id != current_user.id:
        # Verificar se é psicólogo do agendamento
        psychologist = db.query(models.Psychologist).filter(
            models.Psychologist.user_id == current_user.id
        ).first()
        
        if not psychologist or appointment.psychologist_id != psychologist.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view this payment"
            )
    
    return payment

@router.get("/my-payments", response_model=list[schemas.PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    payments = db.query(models.Payment).filter(
        models.Payment.user_id == current_user.id
    ).order_by(models.Payment.created_at.desc()).all()
    
    return payments

@router.post("/{payment_id}/refund", response_model=schemas.PaymentResponse)
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    
    # Verificar permissão
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only refund your own payments"
        )
    
    # Verificar se pode reembolsar
    if payment.status != "paid":
        raise HTTPException(
            status_code=400,
            detail="Only paid payments can be refunded"
        )
    
    # Simular reembolso
    payment.status = "refunded"
    payment.transaction_id = f"{payment.transaction_id}-REFUND"
    
    # Atualizar agendamento
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == payment.appointment_id
    ).first()
    
    if appointment:
        appointment.payment_status = "refunded"
        appointment.status = "cancelled"
    
    db.commit()
    db.refresh(payment)
    
    return payment


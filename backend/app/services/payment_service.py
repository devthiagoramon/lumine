"""
Service para gerenciar pagamentos e saldo
"""
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.psychologist import Psychologist
from app.services.notification_service import NotificationService
from typing import Optional, List
import uuid
import random
import time

class PaymentService:
    @staticmethod
    def process_payment_success(
        db: Session,
        payment: Payment,
        appointment: Appointment
    ):
        """Processa pagamento bem-sucedido e atualiza saldo do psicólogo"""
        # Atualizar saldo do psicólogo (80% para o psicólogo, 20% para a plataforma)
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == appointment.psychologist_id
        ).first()
        
        if psychologist:
            psychologist_share = payment.amount * 0.80  # 80% para o psicólogo
            psychologist.balance = (psychologist.balance or 0.0) + psychologist_share
            db.commit()
            
            # Criar notificação para o psicólogo
            NotificationService.create_notification(
                db=db,
                user_id=psychologist.user_id,
                title="Novo Pagamento Recebido",
                message=f"Você recebeu R$ {psychologist_share:.2f} de uma consulta.",
                type="payment",
                related_id=payment.id,
                related_type="payment"
            )
        
        # Criar notificação para o cliente
        NotificationService.create_notification(
            db=db,
            user_id=appointment.user_id,
            title="Pagamento Confirmado",
            message="Seu pagamento foi processado com sucesso.",
            type="payment",
            related_id=payment.id,
            related_type="payment"
        )
    
    @staticmethod
    def generate_mock_payment_id() -> str:
        """Gera um ID mockado de pagamento"""
        return f"PAY-{uuid.uuid4().hex[:16].upper()}"
    
    @staticmethod
    def generate_mock_transaction_id() -> str:
        """Gera um ID mockado de transação"""
        return f"TXN-{uuid.uuid4().hex[:16].upper()}"
    
    @staticmethod
    def process_mock_payment(payment_method: str, amount: float) -> dict:
        """Simula processamento de pagamento"""
        time.sleep(0.5)  # Simular delay
        success = random.random() > 0.05  # 95% de sucesso
        
        if success:
            return {
                "status": "paid",
                "payment_id": PaymentService.generate_mock_payment_id(),
                "transaction_id": PaymentService.generate_mock_transaction_id(),
                "message": "Pagamento processado com sucesso"
            }
        else:
            return {
                "status": "failed",
                "payment_id": PaymentService.generate_mock_payment_id(),
                "transaction_id": None,
                "message": "Falha no processamento do pagamento. Tente novamente."
            }
    
    @staticmethod
    def create_payment(
        db: Session,
        appointment_id: int,
        user_id: int,
        payment_data: dict
    ) -> Payment:
        """Criar pagamento"""
        payment = Payment(
            appointment_id=appointment_id,
            user_id=user_id,
            **payment_data
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_payment_by_appointment_id(
        db: Session,
        appointment_id: int
    ) -> Optional[Payment]:
        """Obter pagamento por appointment_id"""
        return db.query(Payment).filter(
            Payment.appointment_id == appointment_id
        ).first()
    
    @staticmethod
    def get_payments_by_user(
        db: Session,
        user_id: int
    ) -> List[Payment]:
        """Obter pagamentos do usuário"""
        return db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_financial_history(
        db: Session,
        psychologist_id: int
    ) -> List[Payment]:
        """Obter histórico financeiro do psicólogo"""
        appointments = db.query(Appointment).filter(
            Appointment.psychologist_id == psychologist_id
        ).all()
        
        appointment_ids = [app.id for app in appointments]
        
        return db.query(Payment).filter(
            Payment.appointment_id.in_(appointment_ids),
            Payment.status == 'paid'
        ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def refund_payment(
        db: Session,
        payment_id: int,
        user_id: int
    ) -> Optional[Payment]:
        """Reembolsar pagamento"""
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == user_id
        ).first()
        
        if not payment or payment.status != "paid":
            return None
        
        payment.status = "refunded"
        payment.transaction_id = f"{payment.transaction_id}-REFUND" if payment.transaction_id else "REFUND"
        
        # Atualizar agendamento
        appointment = db.query(Appointment).filter(
            Appointment.id == payment.appointment_id
        ).first()
        
        if appointment:
            appointment.payment_status = "refunded"
            appointment.status = "cancelled"
        
        db.commit()
        db.refresh(payment)
        
        return payment


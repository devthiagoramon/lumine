"""
Service para gerenciar saques
"""
from sqlalchemy.orm import Session
from app.models.withdrawal import Withdrawal
from app.models.psychologist import Psychologist
from typing import List, Optional
from datetime import datetime

class WithdrawalService:
    @staticmethod
    def create_withdrawal(
        db: Session,
        psychologist_id: int,
        withdrawal_data: dict
    ) -> Withdrawal:
        """Criar solicitação de saque"""
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == psychologist_id
        ).first()
        
        if not psychologist:
            return None
        
        # Verificar saldo
        balance = psychologist.balance or 0.0
        amount = withdrawal_data['amount']
        
        if amount > balance:
            return None
        
        # Criar saque
        withdrawal = Withdrawal(psychologist_id=psychologist_id, **withdrawal_data)
        db.add(withdrawal)
        
        # Reservar valor (subtrair do saldo)
        psychologist.balance = balance - amount
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def get_withdrawals_by_psychologist(
        db: Session,
        psychologist_id: int
    ) -> List[Withdrawal]:
        """Obter saques do psicólogo"""
        return db.query(Withdrawal).filter(
            Withdrawal.psychologist_id == psychologist_id
        ).order_by(Withdrawal.created_at.desc()).all()
    
    @staticmethod
    def get_withdrawal_by_id(
        db: Session,
        withdrawal_id: int,
        psychologist_id: int
    ) -> Optional[Withdrawal]:
        """Obter saque por ID"""
        return db.query(Withdrawal).filter(
            Withdrawal.id == withdrawal_id,
            Withdrawal.psychologist_id == psychologist_id
        ).first()
    
    @staticmethod
    def process_withdrawal(
        db: Session,
        withdrawal_id: int
    ) -> Withdrawal:
        """Processar saque (aprovar)"""
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.id == withdrawal_id
        ).first()
        
        if withdrawal and withdrawal.status == 'pending':
            withdrawal.status = 'completed'
            withdrawal.processed_at = datetime.now()
            db.commit()
            db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def reject_withdrawal(
        db: Session,
        withdrawal_id: int,
        rejection_reason: str
    ) -> Withdrawal:
        """Rejeitar saque e devolver valor"""
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.id == withdrawal_id
        ).first()
        
        if not withdrawal or withdrawal.status != 'pending':
            return None
        
        # Devolver valor ao saldo
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == withdrawal.psychologist_id
        ).first()
        
        if psychologist:
            psychologist.balance = (psychologist.balance or 0.0) + withdrawal.amount
        
        withdrawal.status = 'rejected'
        withdrawal.rejection_reason = rejection_reason
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal


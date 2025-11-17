"""
Service para gerenciar agendamentos
"""
from sqlalchemy.orm import Session, joinedload
from app.models.appointment import Appointment
from app.models.psychologist import Psychologist
from app.models.user import User
from app.services.notification_service import NotificationService
from typing import Optional, List
from datetime import datetime

class AppointmentService:
    @staticmethod
    def confirm_appointment(
        db: Session,
        appointment_id: int,
        psychologist_id: int
    ) -> Optional[Appointment]:
        """Confirma um agendamento"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.psychologist_id == psychologist_id
        ).first()
        
        if not appointment:
            return None
        
        appointment.status = 'confirmed'
        db.commit()
        db.refresh(appointment)
        
        # Criar notificação para o cliente
        NotificationService.create_notification(
            db=db,
            user_id=appointment.user_id,
            title="Agendamento Confirmado",
            message=f"Seu agendamento foi confirmado pelo psicólogo.",
            type="appointment",
            related_id=appointment.id,
            related_type="appointment"
        )
        
        return appointment
    
    @staticmethod
    def reject_appointment(
        db: Session,
        appointment_id: int,
        psychologist_id: int,
        rejection_reason: str
    ) -> Optional[Appointment]:
        """Recusa um agendamento"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.psychologist_id == psychologist_id
        ).first()
        
        if not appointment:
            return None
        
        appointment.status = 'rejected'
        appointment.rejection_reason = rejection_reason
        db.commit()
        db.refresh(appointment)
        
        # Criar notificação para o cliente
        NotificationService.create_notification(
            db=db,
            user_id=appointment.user_id,
            title="Agendamento Recusado",
            message=f"Seu agendamento foi recusado. Motivo: {rejection_reason}",
            type="appointment",
            related_id=appointment.id,
            related_type="appointment"
        )
        
        return appointment
    
    @staticmethod
    def create_appointment(
        db: Session,
        psychologist_id: int,
        user_id: int,
        appointment_data: dict
    ) -> Appointment:
        """Criar agendamento"""
        appointment = Appointment(
            psychologist_id=psychologist_id,
            user_id=user_id,
            status='pending',
            **appointment_data
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment
    
    @staticmethod
    def get_appointment_by_id(
        db: Session,
        appointment_id: int,
        load_relationships: bool = True
    ) -> Optional[Appointment]:
        """Obter agendamento por ID"""
        query = db.query(Appointment)
        if load_relationships:
            query = query.options(
                joinedload(Appointment.psychologist).joinedload(Psychologist.user),
                joinedload(Appointment.psychologist).joinedload(Psychologist.specialties),
                joinedload(Appointment.psychologist).joinedload(Psychologist.approaches),
                joinedload(Appointment.user)
            )
        return query.filter(Appointment.id == appointment_id).first()
    
    @staticmethod
    def get_appointments_by_user(
        db: Session,
        user_id: int,
        status_filter: Optional[str] = None,
        load_relationships: bool = True
    ) -> List[Appointment]:
        """Obter agendamentos do usuário"""
        query = db.query(Appointment)
        if load_relationships:
            query = query.options(
                joinedload(Appointment.psychologist).joinedload(Psychologist.user),
                joinedload(Appointment.psychologist).joinedload(Psychologist.specialties),
                joinedload(Appointment.psychologist).joinedload(Psychologist.approaches),
                joinedload(Appointment.user)
            )
        query = query.filter(Appointment.user_id == user_id)
        
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        
        return query.order_by(Appointment.appointment_date.asc()).all()
    
    @staticmethod
    def get_appointments_by_psychologist(
        db: Session,
        psychologist_id: int,
        status_filter: Optional[str] = None,
        load_relationships: bool = True
    ) -> List[Appointment]:
        """Obter agendamentos do psicólogo"""
        query = db.query(Appointment)
        if load_relationships:
            query = query.options(
                joinedload(Appointment.psychologist).joinedload(Psychologist.user),
                joinedload(Appointment.psychologist).joinedload(Psychologist.specialties),
                joinedload(Appointment.psychologist).joinedload(Psychologist.approaches),
                joinedload(Appointment.user)
            )
        query = query.filter(Appointment.psychologist_id == psychologist_id)
        
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        
        return query.order_by(Appointment.appointment_date.asc()).all()
    
    @staticmethod
    def update_appointment(
        db: Session,
        appointment: Appointment,
        update_data: dict
    ) -> Appointment:
        """Atualizar agendamento"""
        for field, value in update_data.items():
            setattr(appointment, field, value)
        db.commit()
        db.refresh(appointment)
        return appointment
    
    @staticmethod
    def delete_appointment(
        db: Session,
        appointment_id: int,
        user_id: int
    ) -> bool:
        """Deletar agendamento"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id
        ).first()
        
        if not appointment:
            return False
        
        db.delete(appointment)
        db.commit()
        return True
    
    @staticmethod
    def validate_appointment_date(appointment_date: datetime) -> bool:
        """Validar se data é futura"""
        from datetime import timezone
        # Garantir que ambos os datetimes tenham timezone
        if appointment_date.tzinfo is None:
            # Se appointment_date não tem timezone, assumir UTC
            appointment_date = appointment_date.replace(tzinfo=timezone.utc)
        # Usar datetime.utcnow() com timezone para comparação
        now = datetime.now(timezone.utc)
        return appointment_date > now
    
    @staticmethod
    def validate_consultation_type(
        psychologist: Psychologist,
        appointment_type: str
    ) -> bool:
        """Validar tipo de consulta"""
        if appointment_type == 'online':
            return psychologist.online_consultation
        elif appointment_type == 'presencial':
            return psychologist.in_person_consultation
        return False

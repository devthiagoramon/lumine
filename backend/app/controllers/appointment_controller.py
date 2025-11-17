"""
Appointment Controller - Endpoints de agendamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import auth
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar agendamento"""
    # Verificar se psicólogo existe
    psychologist = db.query(Psychologist).filter(
        Psychologist.id == appointment.psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Validar data
    if not AppointmentService.validate_appointment_date(appointment.appointment_date):
        raise HTTPException(
            status_code=400,
            detail="Appointment date must be in the future"
        )
    
    # Validar tipo de consulta
    if not AppointmentService.validate_consultation_type(psychologist, appointment.appointment_type):
        consultation_type = "online" if appointment.appointment_type == 'online' else "presencial"
        raise HTTPException(
            status_code=400,
            detail=f"This psychologist does not offer {consultation_type} consultations"
        )
    
    # Criar agendamento usando service
    appointment_data = {
        "appointment_date": appointment.appointment_date,
        "appointment_type": appointment.appointment_type,
        "notes": appointment.notes
    }
    db_appointment = AppointmentService.create_appointment(
        db=db,
        psychologist_id=appointment.psychologist_id,
        user_id=current_user.id,
        appointment_data=appointment_data
    )
    
    # Criar notificação para o psicólogo
    NotificationService.create_notification(
        db=db,
        user_id=psychologist.user_id,
        title="Novo Agendamento Solicitado",
        message=f"Você recebeu uma nova solicitação de agendamento de {current_user.full_name}.",
        type="appointment",
        related_id=db_appointment.id,
        related_type="appointment"
    )
    
    # Recarregar com relacionamentos
    db_appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=db_appointment.id,
        load_relationships=True
    )
    
    return db_appointment

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meus agendamentos"""
    appointments = AppointmentService.get_appointments_by_user(
        db=db,
        user_id=current_user.id,
        status_filter=status_filter,
        load_relationships=True
    )
    return appointments

@router.get("/psychologist-appointments", response_model=List[AppointmentResponse])
def get_psychologist_appointments(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter agendamentos do psicólogo"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view their appointments"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    appointments = AppointmentService.get_appointments_by_psychologist(
        db=db,
        psychologist_id=psychologist.id,
        status_filter=status_filter,
        load_relationships=True
    )
    
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter agendamento por ID"""
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        load_relationships=True
    )
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Verificar permissão
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if appointment.user_id != current_user.id and (not psychologist or appointment.psychologist_id != psychologist.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this appointment"
        )
    
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Atualizar agendamento"""
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        load_relationships=False
    )
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Verificar permissão
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    can_update = (
        appointment.user_id == current_user.id or
        (psychologist and appointment.psychologist_id == psychologist.id)
    )
    
    if not can_update:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this appointment"
        )
    
    # Atualizar usando service
    update_data = appointment_update.dict(exclude_unset=True)
    db_appointment = AppointmentService.update_appointment(
        db=db,
        appointment=appointment,
        update_data=update_data
    )
    
    # Recarregar com relacionamentos
    db_appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        load_relationships=True
    )
    
    return db_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Deletar agendamento"""
    success = AppointmentService.delete_appointment(
        db=db,
        appointment_id=appointment_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    return None

@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Confirmar agendamento (apenas psicólogo)"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can confirm appointments"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    appointment = AppointmentService.confirm_appointment(
        db=db,
        appointment_id=appointment_id,
        psychologist_id=psychologist.id
    )
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Recarregar com relacionamentos
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        load_relationships=True
    )
    
    return appointment

@router.post("/{appointment_id}/reject", response_model=AppointmentResponse)
def reject_appointment(
    appointment_id: int,
    rejection_reason: str = Query(..., description="Motivo da recusa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Recusar agendamento (apenas psicólogo)"""
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can reject appointments"
        )
    
    psychologist = db.query(Psychologist).filter(
        Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    appointment = AppointmentService.reject_appointment(
        db=db,
        appointment_id=appointment_id,
        psychologist_id=psychologist.id,
        rejection_reason=rejection_reason
    )
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Recarregar com relacionamentos
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        load_relationships=True
    )
    
    return appointment


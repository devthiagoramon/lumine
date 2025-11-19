from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app import auth, schemas, models

router = APIRouter()

@router.post("/", response_model=schemas.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se psicólogo existe
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == appointment.psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Verificar se data é futura
    # Pydantic já converte a string ISO para datetime
    # Garantir que ambos tenham timezone para comparação
    now_utc = datetime.now(timezone.utc)
    
    # Processar a data do agendamento
    appointment_date = appointment.appointment_date
    
    # Se a data não tem timezone, assumir que é UTC
    if appointment_date.tzinfo is None:
        appointment_date_utc = appointment_date.replace(tzinfo=timezone.utc)
    else:
        appointment_date_utc = appointment_date.astimezone(timezone.utc)
    
    # Verificar se a data é no futuro
    if appointment_date_utc <= now_utc:
        raise HTTPException(
            status_code=400,
            detail="A data do agendamento deve ser no futuro"
        )
    
    # Verificar tipo de consulta
    if appointment.appointment_type == 'online' and not psychologist.online_consultation:
        raise HTTPException(
            status_code=400,
            detail="This psychologist does not offer online consultations"
        )
    
    if appointment.appointment_type == 'presencial' and not psychologist.in_person_consultation:
        raise HTTPException(
            status_code=400,
            detail="This psychologist does not offer in-person consultations"
        )
    
    # Criar agendamento
    # Usar a data com timezone que foi validada
    db_appointment = models.Appointment(
        psychologist_id=appointment.psychologist_id,
        user_id=current_user.id,
        appointment_date=appointment_date_utc,
        appointment_type=appointment.appointment_type,
        notes=appointment.notes,
        status='pending'
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Recarregar com relacionamentos
    db_appointment = db.query(models.Appointment).options(
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.user),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.specialties),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.approaches),
        joinedload(models.Appointment.user)
    ).filter(models.Appointment.id == db_appointment.id).first()
    
    return db_appointment

@router.get("/my-appointments", response_model=List[schemas.AppointmentResponse])
def get_my_appointments(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Appointment).options(
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.user),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.specialties),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.approaches),
        joinedload(models.Appointment.user)
    ).filter(
        models.Appointment.user_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(models.Appointment.status == status_filter)
    
    appointments = query.order_by(
        models.Appointment.appointment_date.asc()
    ).all()
    
    return appointments

@router.get("/psychologist-appointments", response_model=List[schemas.AppointmentResponse])
def get_psychologist_appointments(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se é psicólogo
    if not current_user.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view their appointments"
        )
    
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.user_id == current_user.id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    query = db.query(models.Appointment).options(
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.user),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.specialties),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.approaches),
        joinedload(models.Appointment.user)
    ).filter(
        models.Appointment.psychologist_id == psychologist.id
    )
    
    if status_filter:
        query = query.filter(models.Appointment.status == status_filter)
    
    appointments = query.order_by(
        models.Appointment.appointment_date.asc()
    ).all()
    
    return appointments

@router.get("/{appointment_id}", response_model=schemas.AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    appointment = db.query(models.Appointment).options(
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.user),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.specialties),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.approaches),
        joinedload(models.Appointment.user)
    ).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Verificar se usuário tem permissão
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.user_id == current_user.id
    ).first()
    
    if appointment.user_id != current_user.id and (not psychologist or appointment.psychologist_id != psychologist.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this appointment"
        )
    
    return appointment

@router.put("/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Verificar permissão
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.user_id == current_user.id
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
    
    # Atualizar campos
    update_data = appointment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    # Recarregar com relacionamentos
    appointment = db.query(models.Appointment).options(
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.user),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.specialties),
        joinedload(models.Appointment.psychologist).joinedload(models.Psychologist.approaches),
        joinedload(models.Appointment.user)
    ).filter(models.Appointment.id == appointment_id).first()
    
    return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    # Apenas o cliente pode cancelar
    if appointment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the client can cancel an appointment"
        )
    
    db.delete(appointment)
    db.commit()
    
    return None


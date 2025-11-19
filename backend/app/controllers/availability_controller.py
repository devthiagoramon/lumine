"""
Availability Controller - Endpoints de disponibilidade
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistAvailabilityCreate, PsychologistAvailabilityUpdate,
    PsychologistAvailabilityResponse
)
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.psychologist_availability import PsychologistAvailability
from app.models.appointment import Appointment
from datetime import datetime, date, timedelta, time as dt_time, timezone

router = APIRouter()

@router.post("/", response_model=PsychologistAvailabilityResponse, status_code=status.HTTP_201_CREATED)
def criar_disponibilidade(
    disponibilidade: PsychologistAvailabilityCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar horário de disponibilidade"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create availability"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    # Validar dia da semana
    if disponibilidade.day_of_week < 0 or disponibilidade.day_of_week > 6:
        raise HTTPException(
            status_code=400,
            detail="day_of_week must be between 0 (Monday) and 6 (Sunday)"
        )
    
    # Verificar se já existe disponibilidade para este dia
    existing_availability = PsychologistAvailability.verificar_existente(
        db, psychologist.id, disponibilidade.day_of_week
    )
    
    if existing_availability:
        raise HTTPException(
            status_code=400,
            detail="Availability for this day already exists. Use update instead."
        )
    
    db_availability = PsychologistAvailability.criar(
        db,
        psychologist_id=psychologist.id,
        day_of_week=disponibilidade.day_of_week,
        start_time=disponibilidade.start_time,
        end_time=disponibilidade.end_time,
        is_available=disponibilidade.is_available if hasattr(disponibilidade, 'is_available') else True
    )
    
    return db_availability

@router.get("/", response_model=List[PsychologistAvailabilityResponse])
def obter_minha_disponibilidade(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter horários de disponibilidade do psicólogo logado"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can view availability"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    availability = PsychologistAvailability.listar_por_psicologo(db, psychologist.id)
    
    return availability

@router.get("/psychologist/{id_psicologo}", response_model=List[PsychologistAvailabilityResponse])
def obter_disponibilidade_psicologo(
    id_psicologo: int,
    db: Session = Depends(get_db)
):
    """Obter horários de disponibilidade de um psicólogo"""
    psychologist = Psychologist.obter_por_id(db, id_psicologo)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    availability = PsychologistAvailability.listar_por_psicologo(db, id_psicologo, apenas_disponiveis=True)
    
    return availability

@router.put("/{id_disponibilidade}", response_model=PsychologistAvailabilityResponse)
def atualizar_disponibilidade(
    id_disponibilidade: int,
    atualizacao_disponibilidade: PsychologistAvailabilityUpdate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar horário de disponibilidade"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can update availability"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    availability = PsychologistAvailability.obter_por_id(db, id_disponibilidade, psychologist_id=psychologist.id)
    
    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability not found"
        )
    
    update_data = atualizacao_disponibilidade.dict(exclude_unset=True)
    availability.atualizar(db, **update_data)
    
    return availability

@router.delete("/{id_disponibilidade}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_disponibilidade(
    id_disponibilidade: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar horário de disponibilidade"""
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can delete availability"
        )
    
    psychologist = Psychologist.obter_por_user_id(db, usuario_atual.id)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist profile not found"
        )
    
    availability = PsychologistAvailability.obter_por_id(db, id_disponibilidade, psychologist_id=psychologist.id)
    
    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability not found"
        )
    
    availability.deletar(db)
    return None

@router.get("/psychologist/{id_psicologo}/available-slots")
def obter_horarios_disponiveis(
    id_psicologo: int,
    data_inicio: str,  # Formato YYYY-MM-DD
    data_fim: str,  # Formato YYYY-MM-DD
    tipo_agendamento: str = "online",
    db: Session = Depends(get_db)
):
    """Obter horários disponíveis para agendamento"""
    from datetime import date as date_type
    
    try:
        start = date_type.fromisoformat(data_inicio)
        end = date_type.fromisoformat(data_fim)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Verificar se psicólogo existe
    psychologist = Psychologist.obter_por_id(db, id_psicologo)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Validar período (máximo 3 meses)
    if (end - start).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 90 days"
        )
    
    # Obter disponibilidade semanal do psicólogo
    weekly_availability = PsychologistAvailability.listar_por_psicologo(db, id_psicologo, apenas_disponiveis=True)
    
    if not weekly_availability:
        slots = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        appointments = Appointment.listar_por_psicologo(db, id_psicologo)
        # Filtrar por período e status
        appointments = [
            apt for apt in appointments
            if apt.appointment_date >= datetime.combine(start, dt_time.min) and
               apt.appointment_date <= datetime.combine(end, dt_time.max) and
               apt.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        booked_slots = set()
        for apt in appointments:
            apt_date = apt.appointment_date.date()
            apt_time = apt.appointment_date.time()
            booked_slots.add((apt_date, apt_time))
        
        # Gerar slots disponíveis
        slots = []
        current_date = start
        
        while current_date <= end:
            day_of_week = current_date.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            day_availability = [
                av for av in weekly_availability
                if av.day_of_week == day_of_week
            ]
            
            for av in day_availability:
                # Parse dos horários
                start_time = datetime.strptime(av.start_time, "%H:%M").time()
                end_time = datetime.strptime(av.end_time, "%H:%M").time()
                
                # Gerar slots de 1 hora
                current_time = start_time
                
                while current_time < end_time:
                    # Calcular próximo horário (1 hora depois)
                    current_datetime = datetime.combine(current_date, current_time)
                    next_datetime = current_datetime + timedelta(hours=1)
                    next_time = next_datetime.time()
                    
                    # Verificar se o próximo horário não ultrapassa o fim
                    if next_time > end_time:
                        break
                    
                    # Verificar se o slot não está ocupado
                    slot_key = (current_date, current_time)
                    if slot_key not in booked_slots:
                        # Verificar se não é no passado
                        slot_datetime = datetime.combine(current_date, current_time)
                        if slot_datetime.tzinfo is None:
                            slot_datetime = slot_datetime.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        if slot_datetime > now:
                            slots.append({
                                "date": current_date.isoformat(),
                                "time": current_time.strftime("%H:%M"),
                                "datetime": slot_datetime.isoformat(),
                                "available": True
                            })
                    
                    current_time = next_time
            
            current_date += timedelta(days=1)
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": data_inicio,
        "end_date": data_fim,
        "appointment_type": tipo_agendamento,
        "available_slots": slots,
        "total_slots": len(slots)
    }

@router.get("/psychologist/{id_psicologo}/available-dates")
def obter_datas_disponiveis(
    id_psicologo: int,
    data_inicio: str,  # Formato YYYY-MM-DD
    data_fim: str,  # Formato YYYY-MM-DD
    tipo_agendamento: str = "online",
    db: Session = Depends(get_db)
):
    """Obter datas com horários disponíveis (para calendário)"""
    from datetime import date as date_type
    
    try:
        start = date_type.fromisoformat(data_inicio)
        end = date_type.fromisoformat(data_fim)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Verificar se psicólogo existe
    psychologist = Psychologist.obter_por_id(db, id_psicologo)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Validar período (máximo 3 meses)
    if (end - start).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 90 days"
        )
    
    # Obter slots disponíveis
    weekly_availability = PsychologistAvailability.listar_por_psicologo(db, id_psicologo, apenas_disponiveis=True)
    
    if not weekly_availability:
        dates = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        appointments = Appointment.listar_por_psicologo(db, id_psicologo)
        # Filtrar por período e status
        appointments = [
            apt for apt in appointments
            if apt.appointment_date >= datetime.combine(start, dt_time.min) and
               apt.appointment_date <= datetime.combine(end, dt_time.max) and
               apt.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        booked_slots = set()
        for apt in appointments:
            apt_date = apt.appointment_date.date()
            apt_time = apt.appointment_date.time()
            booked_slots.add((apt_date, apt_time))
        
        # Gerar slots disponíveis
        slots = []
        current_date = start
        
        while current_date <= end:
            day_of_week = current_date.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            day_availability = [
                av for av in weekly_availability
                if av.day_of_week == day_of_week
            ]
            
            for av in day_availability:
                # Parse dos horários
                start_time = datetime.strptime(av.start_time, "%H:%M").time()
                end_time = datetime.strptime(av.end_time, "%H:%M").time()
                
                # Gerar slots de 1 hora
                current_time = start_time
                
                while current_time < end_time:
                    # Calcular próximo horário (1 hora depois)
                    current_datetime = datetime.combine(current_date, current_time)
                    next_datetime = current_datetime + timedelta(hours=1)
                    next_time = next_datetime.time()
                    
                    # Verificar se o próximo horário não ultrapassa o fim
                    if next_time > end_time:
                        break
                    
                    # Verificar se o slot não está ocupado
                    slot_key = (current_date, current_time)
                    if slot_key not in booked_slots:
                        # Verificar se não é no passado
                        slot_datetime = datetime.combine(current_date, current_time)
                        if slot_datetime.tzinfo is None:
                            slot_datetime = slot_datetime.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        if slot_datetime > now:
                            slots.append({
                                "date": current_date.isoformat(),
                                "time": current_time.strftime("%H:%M"),
                                "datetime": slot_datetime.isoformat(),
                                "available": True
                            })
                    
                    current_time = next_time
            
            current_date += timedelta(days=1)
        
        # Agrupar por data
        dates_dict = {}
        for slot in slots:
            slot_date = slot["date"]
            if slot_date not in dates_dict:
                dates_dict[slot_date] = {
                    "date": slot_date,
                    "available_slots": [],
                    "count": 0
                }
            dates_dict[slot_date]["available_slots"].append(slot["time"])
            dates_dict[slot_date]["count"] += 1
        
        dates = list(dates_dict.values())
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": data_inicio,
        "end_date": data_fim,
        "appointment_type": tipo_agendamento,
        "available_dates": dates,
        "total_dates": len(dates)
    }


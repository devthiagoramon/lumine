"""
Availability Controller - Endpoints de disponibilidade
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
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
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar horário de disponibilidade"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can create availability"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    # Validar dia da semana
    if disponibilidade.day_of_week < 0 or disponibilidade.day_of_week > 6:
        raise HTTPException(
            status_code=400,
            detail="Dia da semana deve estar entre 0 (Segunda) e 6 (Domingo)"
        )
    
    # Verificar se já existe disponibilidade para este dia
    disponibilidade_existente = PsychologistAvailability.verificar_existente(
        psicologo.id, disponibilidade.day_of_week
    )
    
    if disponibilidade_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe disponibilidade para este dia. Use atualização ao invés."
        )
    
    disponibilidade_created = PsychologistAvailability.criar(
        psychologist_id=psicologo.id,
        day_of_week=disponibilidade.day_of_week,
        start_time=disponibilidade.start_time,
        end_time=disponibilidade.end_time,
        is_available=disponibilidade.is_available if hasattr(disponibilidade, 'is_available') else True
    )
    
    return disponibilidade_created

@router.get("/", response_model=List[PsychologistAvailabilityResponse])
def obter_minha_disponibilidade(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter horários de disponibilidade do psicólogo logado"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar disponibilidade"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    disponibilidades = PsychologistAvailability.listar_por_psicologo(psicologo.id)
    
    return disponibilidades

@router.get("/psychologist/{id_psicologo}", response_model=List[PsychologistAvailabilityResponse])
def obter_disponibilidade_psicologo(
    id_psicologo: int
):
    """Obter horários de disponibilidade de um psicólogo"""
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    disponibilidades = PsychologistAvailability.listar_por_psicologo(id_psicologo, apenas_disponiveis=True)
    
    return disponibilidades

@router.put("/{id_disponibilidade}", response_model=PsychologistAvailabilityResponse)
def atualizar_disponibilidade(
    id_disponibilidade: int,
    atualizacao_disponibilidade: PsychologistAvailabilityUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar horário de disponibilidade"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem atualizar disponibilidade"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    disponibilidade = PsychologistAvailability.obter_por_id(id_disponibilidade, id_psicologo=psicologo.id)
    
    if not disponibilidade:
        raise HTTPException(
            status_code=404,
            detail="Disponibilidade não encontrada"
        )
    
    dados_atualizacao = atualizacao_disponibilidade.dict(exclude_unset=True)
    disponibilidade.atualizar(**dados_atualizacao)
    
    return disponibilidade

@router.delete("/{id_disponibilidade}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_disponibilidade(
    id_disponibilidade: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar horário de disponibilidade"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem deletar disponibilidade"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    disponibilidade = PsychologistAvailability.obter_por_id(id_disponibilidade, id_psicologo=psicologo.id)
    
    if not disponibilidade:
        raise HTTPException(
            status_code=404,
            detail="Disponibilidade não encontrada"
        )
    
    disponibilidade.deletar()
    return None

@router.get("/psychologist/{id_psicologo}/available-slots")
def obter_horarios_disponiveis(
    id_psicologo: int,
    data_inicio: str,  # Formato YYYY-MM-DD
    data_fim: str,  # Formato YYYY-MM-DD
    tipo_agendamento: str = "online"
):
    """Obter horários disponíveis para agendamento"""
    from datetime import date as date_type
    
    try:
        data_inicio_obj = date_type.fromisoformat(data_inicio)
        data_fim_obj = date_type.fromisoformat(data_fim)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Validar período (máximo 3 meses)
    if (data_fim_obj - data_inicio_obj).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Período não pode exceder 90 dias"
        )
    
    # Obter disponibilidade semanal do psicólogo
    disponibilidade_semanal = PsychologistAvailability.listar_por_psicologo(id_psicologo, apenas_disponiveis=True)
    
    if not disponibilidade_semanal:
        horarios = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        agendamentos = Appointment.listar_por_psicologo(id_psicologo)
        # Filtrar por período e status
        agendamentos = [
            agendamento for agendamento in agendamentos
            if agendamento.appointment_date >= datetime.combine(data_inicio_obj, dt_time.min) and
               agendamento.appointment_date <= datetime.combine(data_fim_obj, dt_time.max) and
               agendamento.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        slots_reservados = set()
        for agendamento in agendamentos:
            data_agendamento = agendamento.appointment_date.date()
            horario_agendamento = agendamento.appointment_date.time()
            slots_reservados.add((data_agendamento, horario_agendamento))
        
        # Gerar slots disponíveis
        horarios = []
        data_atual = data_inicio_obj
        
        while data_atual <= data_fim_obj:
            dia_da_semana = data_atual.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            disponibilidade_dia = [
                disponibilidade for disponibilidade in disponibilidade_semanal
                if disponibilidade.day_of_week == dia_da_semana
            ]
            
            for disponibilidade in disponibilidade_dia:
                # Parse dos horários
                horario_inicio = datetime.strptime(disponibilidade.start_time, "%H:%M").time()
                horario_fim = datetime.strptime(disponibilidade.end_time, "%H:%M").time()
                
                # Gerar slots de 1 hora
                horario_atual = horario_inicio
                
                while horario_atual < horario_fim:
                    # Calcular próximo horário (1 hora depois)
                    data_hora_atual = datetime.combine(data_atual, horario_atual)
                    proxima_data_hora = data_hora_atual + timedelta(hours=1)
                    proximo_horario = proxima_data_hora.time()
                    
                    # Verificar se o próximo horário não ultrapassa o fim
                    if proximo_horario > horario_fim:
                        break
                    
                    # Verificar se o slot não está ocupado
                    chave_slot = (data_atual, horario_atual)
                    if chave_slot not in slots_reservados:
                        # Verificar se não é no passado
                        data_hora_slot = datetime.combine(data_atual, horario_atual)
                        if data_hora_slot.tzinfo is None:
                            data_hora_slot = data_hora_slot.replace(tzinfo=timezone.utc)
                        agora = datetime.now(timezone.utc)
                        if data_hora_slot > agora:
                            horarios.append({
                                "date": data_atual.isoformat(),
                                "time": horario_atual.strftime("%H:%M"),
                                "datetime": data_hora_slot.isoformat(),
                                "available": True
                            })
                    
                    horario_atual = proximo_horario
            
            data_atual += timedelta(days=1)
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": data_inicio,
        "end_date": data_fim,
        "appointment_type": tipo_agendamento,
        "available_slots": horarios,
        "total_slots": len(horarios)
    }

@router.get("/psychologist/{id_psicologo}/available-dates")
def obter_datas_disponiveis(
    id_psicologo: int,
    data_inicio: str,  # Formato YYYY-MM-DD
    data_fim: str,  # Formato YYYY-MM-DD
    tipo_agendamento: str = "online"
):
    """Obter datas com horários disponíveis (para calendário)"""
    from datetime import date as date_type
    
    try:
        data_inicio_obj = date_type.fromisoformat(data_inicio)
        data_fim_obj = date_type.fromisoformat(data_fim)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Validar período (máximo 3 meses)
    if (data_fim_obj - data_inicio_obj).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Período não pode exceder 90 dias"
        )
    
    # Obter slots disponíveis
    disponibilidade_semanal = PsychologistAvailability.listar_por_psicologo(id_psicologo, apenas_disponiveis=True)
    
    if not disponibilidade_semanal:
        datas = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        agendamentos = Appointment.listar_por_psicologo(id_psicologo)
        # Filtrar por período e status
        agendamentos = [
            agendamento for agendamento in agendamentos
            if agendamento.appointment_date >= datetime.combine(data_inicio_obj, dt_time.min) and
               agendamento.appointment_date <= datetime.combine(data_fim_obj, dt_time.max) and
               agendamento.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        slots_reservados = set()
        for agendamento in agendamentos:
            data_agendamento = agendamento.appointment_date.date()
            horario_agendamento = agendamento.appointment_date.time()
            slots_reservados.add((data_agendamento, horario_agendamento))
        
        # Gerar slots disponíveis
        horarios = []
        data_atual = data_inicio_obj
        
        while data_atual <= data_fim_obj:
            dia_da_semana = data_atual.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            disponibilidade_dia = [
                disponibilidade for disponibilidade in disponibilidade_semanal
                if disponibilidade.day_of_week == dia_da_semana
            ]
            
            for disponibilidade in disponibilidade_dia:
                # Parse dos horários
                horario_inicio = datetime.strptime(disponibilidade.start_time, "%H:%M").time()
                horario_fim = datetime.strptime(disponibilidade.end_time, "%H:%M").time()
                
                # Gerar slots de 1 hora
                horario_atual = horario_inicio
                
                while horario_atual < horario_fim:
                    # Calcular próximo horário (1 hora depois)
                    data_hora_atual = datetime.combine(data_atual, horario_atual)
                    proxima_data_hora = data_hora_atual + timedelta(hours=1)
                    proximo_horario = proxima_data_hora.time()
                    
                    # Verificar se o próximo horário não ultrapassa o fim
                    if proximo_horario > horario_fim:
                        break
                    
                    # Verificar se o slot não está ocupado
                    chave_slot = (data_atual, horario_atual)
                    if chave_slot not in slots_reservados:
                        # Verificar se não é no passado
                        data_hora_slot = datetime.combine(data_atual, horario_atual)
                        if data_hora_slot.tzinfo is None:
                            data_hora_slot = data_hora_slot.replace(tzinfo=timezone.utc)
                        agora = datetime.now(timezone.utc)
                        if data_hora_slot > agora:
                            horarios.append({
                                "date": data_atual.isoformat(),
                                "time": horario_atual.strftime("%H:%M"),
                                "datetime": data_hora_slot.isoformat(),
                                "available": True
                            })
                    
                    horario_atual = proximo_horario
            
            data_atual += timedelta(days=1)
        
        # Agrupar por data
        dicionario_datas = {}
        for horario in horarios:
            data_slot = horario["date"]
            if data_slot not in dicionario_datas:
                dicionario_datas[data_slot] = {
                    "date": data_slot,
                    "available_slots": [],
                    "count": 0
                }
            dicionario_datas[data_slot]["available_slots"].append(horario["time"])
            dicionario_datas[data_slot]["count"] += 1
        
        datas = list(dicionario_datas.values())
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": data_inicio,
        "end_date": data_fim,
        "appointment_type": tipo_agendamento,
        "available_dates": datas,
        "total_dates": len(datas)
    }


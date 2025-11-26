"""
Availability Controller - Endpoints de disponibilidade
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List
from app import auth
from app.schemas import (
    PsychologistAvailabilityCreate, PsychologistAvailabilityUpdate,
    PsychologistAvailabilityResponse
)
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.disponibilidade_psicologo import PsychologistAvailability
from app.models.agendamento import Appointment
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
        # Se já existe, atualizar ao invés de criar
        disponibilidade_existente.atualizar(
            horario_inicio=disponibilidade.start_time,
            horario_fim=disponibilidade.end_time,
            esta_disponivel=disponibilidade.is_available if hasattr(disponibilidade, 'is_available') else True
        )
        disponibilidade_created = disponibilidade_existente
    else:
        # Criar nova disponibilidade
        disponibilidade_created = PsychologistAvailability.criar(
            id_psicologo=psicologo.id,
            dia_da_semana=disponibilidade.day_of_week,
            horario_inicio=disponibilidade.start_time,
            horario_fim=disponibilidade.end_time,
            esta_disponivel=disponibilidade.is_available if hasattr(disponibilidade, 'is_available') else True
        )
    
    # Recarregar para garantir dados atualizados
    disponibilidade_created = PsychologistAvailability.obter_por_id(disponibilidade_created.id, id_psicologo=psicologo.id)
    
    # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
    try:
        # Pydantic v2
        response_obj = PsychologistAvailabilityResponse.model_validate(disponibilidade_created)
        serialized = response_obj.model_dump(by_alias=False, mode='json')
    except AttributeError:
        # Pydantic v1 fallback
        response_obj = PsychologistAvailabilityResponse.from_orm(disponibilidade_created)
        serialized = response_obj.dict(by_alias=False)
    
    return JSONResponse(content=serialized, status_code=status.HTTP_201_CREATED)

@router.get("/")
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
    
    # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
    try:
        # Pydantic v2
        serialized = [
            PsychologistAvailabilityResponse.model_validate(a).model_dump(by_alias=False, mode='json')
            for a in disponibilidades
        ]
    except AttributeError:
        # Pydantic v1 fallback
        serialized = [
            PsychologistAvailabilityResponse.from_orm(a).dict(by_alias=False)
            for a in disponibilidades
        ]
    
    return JSONResponse(content=serialized)

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

@router.put("/{id_disponibilidade}")
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
    
    # Mapear campos do schema para o modelo
    dados_atualizacao = {}
    if atualizacao_disponibilidade.start_time is not None:
        dados_atualizacao['horario_inicio'] = atualizacao_disponibilidade.start_time
    if atualizacao_disponibilidade.end_time is not None:
        dados_atualizacao['horario_fim'] = atualizacao_disponibilidade.end_time
    if atualizacao_disponibilidade.is_available is not None:
        dados_atualizacao['esta_disponivel'] = atualizacao_disponibilidade.is_available
    
    disponibilidade.atualizar(**dados_atualizacao)
    
    # Recarregar disponibilidade atualizada
    disponibilidade = PsychologistAvailability.obter_por_id(id_disponibilidade, id_psicologo=psicologo.id)
    
    # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
    try:
        # Pydantic v2
        response_obj = PsychologistAvailabilityResponse.model_validate(disponibilidade)
        serialized = response_obj.model_dump(by_alias=False, mode='json')
    except AttributeError:
        # Pydantic v1 fallback
        response_obj = PsychologistAvailabilityResponse.from_orm(disponibilidade)
        serialized = response_obj.dict(by_alias=False)
    
    return JSONResponse(content=serialized)

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
    start_date: str = Query(..., description="Data início (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    appointment_type: str = Query("online", description="Tipo de agendamento")
):
    """Obter horários disponíveis para agendamento"""
    from datetime import date as date_type
    
    try:
        data_inicio_obj = date_type.fromisoformat(start_date)
        data_fim_obj = date_type.fromisoformat(end_date)
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
    
    print(f"DEBUG available-slots: Psicólogo {id_psicologo}, Disponibilidades encontradas: {len(disponibilidade_semanal)}")
    for disp in disponibilidade_semanal:
        print(f"  - ID: {disp.id}, Dia: {disp.dia_da_semana}, Horário: {disp.horario_inicio}-{disp.horario_fim}, Disponível: {disp.esta_disponivel}")
    
    if not disponibilidade_semanal:
        horarios = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        agendamentos = Appointment.listar_por_psicologo(id_psicologo)
        # Filtrar por período e status
        agendamentos = [
            agendamento for agendamento in agendamentos
            if agendamento.data_agendamento >= datetime.combine(data_inicio_obj, dt_time.min) and
               agendamento.data_agendamento <= datetime.combine(data_fim_obj, dt_time.max) and
               agendamento.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        slots_reservados = set()
        for agendamento in agendamentos:
            data_agendamento = agendamento.data_agendamento.date()
            horario_agendamento = agendamento.data_agendamento.time()
            slots_reservados.add((data_agendamento, horario_agendamento))
        
        # Gerar slots disponíveis
        horarios = []
        data_atual = data_inicio_obj
        
        while data_atual <= data_fim_obj:
            dia_da_semana = data_atual.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            disponibilidade_dia = [
                disponibilidade for disponibilidade in disponibilidade_semanal
                if disponibilidade.dia_da_semana == dia_da_semana
            ]
            
            for disponibilidade in disponibilidade_dia:
                # Parse dos horários
                horario_inicio = datetime.strptime(disponibilidade.horario_inicio, "%H:%M").time()
                horario_fim = datetime.strptime(disponibilidade.horario_fim, "%H:%M").time()
                
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
                        # Verificar se não é no passado (comparar apenas data, não hora)
                        data_hora_slot = datetime.combine(data_atual, horario_atual)
                        if data_hora_slot.tzinfo is None:
                            data_hora_slot = data_hora_slot.replace(tzinfo=timezone.utc)
                        agora = datetime.now(timezone.utc)
                        agora_date = agora.date()
                        
                        # Se a data for hoje, verificar se o horário ainda não passou
                        # Se a data for futura, incluir o slot
                        is_future_date = data_atual > agora_date
                        is_today_future_time = data_atual == agora_date and data_hora_slot > agora
                        
                        if is_future_date or is_today_future_time:
                            horarios.append({
                                "date": data_atual.isoformat(),
                                "time": horario_atual.strftime("%H:%M"),
                                "datetime": data_hora_slot.isoformat(),
                                "available": True
                            })
                        else:
                            print(f"DEBUG available-dates: Slot {data_atual.isoformat()} {horario_atual} filtrado - data_atual={data_atual}, agora_date={agora_date}, is_future={is_future_date}, is_today_future={is_today_future_time}")
                    
                    horario_atual = proximo_horario
            
            data_atual += timedelta(days=1)
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": start_date,
        "end_date": end_date,
        "appointment_type": appointment_type,
        "available_slots": horarios,
        "total_slots": len(horarios)
    }

@router.get("/psychologist/{id_psicologo}/available-dates")
def obter_datas_disponiveis(
    id_psicologo: int,
    start_date: str = Query(..., description="Data início (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    appointment_type: str = Query("online", description="Tipo de agendamento")
):
    """Obter datas com horários disponíveis (para calendário)"""
    import sys
    print(f"=== DEBUG: Endpoint available-dates CHAMADO ===", file=sys.stderr, flush=True)
    print(f"ID Psicólogo: {id_psicologo}", file=sys.stderr, flush=True)
    print(f"Data início: {start_date}", file=sys.stderr, flush=True)
    print(f"Data fim: {end_date}", file=sys.stderr, flush=True)
    print(f"Tipo agendamento: {appointment_type}", file=sys.stderr, flush=True)
    
    from datetime import date as date_type
    
    try:
        data_inicio_obj = date_type.fromisoformat(start_date)
        data_fim_obj = date_type.fromisoformat(end_date)
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
    
    print(f"DEBUG available-dates: Psicólogo {id_psicologo}, Disponibilidades encontradas: {len(disponibilidade_semanal)}")
    for disp in disponibilidade_semanal:
        print(f"  - ID: {disp.id}, Dia: {disp.dia_da_semana}, Horário: {disp.horario_inicio}-{disp.horario_fim}, Disponível: {disp.esta_disponivel}")
    
    if not disponibilidade_semanal:
        datas = []
    else:
        # Obter agendamentos confirmados/pendentes no período
        agendamentos = Appointment.listar_por_psicologo(id_psicologo)
        # Filtrar por período e status
        agendamentos = [
            agendamento for agendamento in agendamentos
            if agendamento.data_agendamento >= datetime.combine(data_inicio_obj, dt_time.min) and
               agendamento.data_agendamento <= datetime.combine(data_fim_obj, dt_time.max) and
               agendamento.status in ['pending', 'confirmed']
        ]
        
        # Converter agendamentos para set de (date, time) para busca rápida
        slots_reservados = set()
        for agendamento in agendamentos:
            data_agendamento = agendamento.data_agendamento.date()
            horario_agendamento = agendamento.data_agendamento.time()
            slots_reservados.add((data_agendamento, horario_agendamento))
        
        # Gerar slots disponíveis
        horarios = []
        data_atual = data_inicio_obj
        
        while data_atual <= data_fim_obj:
            dia_da_semana = data_atual.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            disponibilidade_dia = [
                disponibilidade for disponibilidade in disponibilidade_semanal
                if disponibilidade.dia_da_semana == dia_da_semana
            ]
            
            for disponibilidade in disponibilidade_dia:
                # Parse dos horários
                horario_inicio = datetime.strptime(disponibilidade.horario_inicio, "%H:%M").time()
                horario_fim = datetime.strptime(disponibilidade.horario_fim, "%H:%M").time()
                
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
                        # Verificar se não é no passado (comparar apenas data, não hora)
                        data_hora_slot = datetime.combine(data_atual, horario_atual)
                        if data_hora_slot.tzinfo is None:
                            data_hora_slot = data_hora_slot.replace(tzinfo=timezone.utc)
                        agora = datetime.now(timezone.utc)
                        agora_date = agora.date()
                        
                        # Se a data for hoje, verificar se o horário ainda não passou
                        # Se a data for futura, incluir o slot
                        is_future_date = data_atual > agora_date
                        is_today_future_time = data_atual == agora_date and data_hora_slot > agora
                        
                        if is_future_date or is_today_future_time:
                            horarios.append({
                                "date": data_atual.isoformat(),
                                "time": horario_atual.strftime("%H:%M"),
                                "datetime": data_hora_slot.isoformat(),
                                "available": True
                            })
                        else:
                            print(f"DEBUG available-dates: Slot {data_atual.isoformat()} {horario_atual} filtrado - data_atual={data_atual}, agora_date={agora_date}, is_future={is_future_date}, is_today_future={is_today_future_time}")
                    
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
    
    print(f"DEBUG available-dates: Retornando {len(datas)} datas disponíveis")
    for data_info in datas:
        print(f"  - Data: {data_info['date']}, Slots: {data_info['count']}")
    
    return {
        "psychologist_id": id_psicologo,
        "start_date": start_date,
        "end_date": end_date,
        "appointment_type": appointment_type,
        "available_dates": datas,
        "total_dates": len(datas)
    }


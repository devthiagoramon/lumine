"""
Appointment Controller - Endpoints de agendamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app import auth
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.agendamento import Appointment
from app.models.notificacao import Notification
from app.models.disponibilidade_psicologo import PsychologistAvailability

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def criar_agendamento(
    agendamento: AppointmentCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar agendamento"""
    import sys
    import traceback
    print(f"=== DEBUG: Criar agendamento CHAMADO ===", file=sys.stderr, flush=True)
    print(f"Psychologist ID: {agendamento.psychologist_id}", file=sys.stderr, flush=True)
    print(f"Appointment date: {agendamento.appointment_date}", file=sys.stderr, flush=True)
    print(f"Appointment type: {agendamento.appointment_type}", file=sys.stderr, flush=True)
    print(f"User ID: {usuario_atual.id}", file=sys.stderr, flush=True)
    
    try:
        # Verificar se psicólogo existe
        psicologo = Psychologist.obter_por_id(agendamento.psychologist_id)
        if not psicologo:
            raise HTTPException(
                status_code=404,
                detail="Psicólogo não encontrado"
            )
        
        # Verificar se psicólogo está verificado (aprovado pelo admin)
        if not psicologo.esta_verificado:
            raise HTTPException(
                status_code=403,
                detail="Este psicólogo ainda não foi verificado pela administração. Agendamentos só podem ser feitos com psicólogos verificados."
            )
        
        # Validar data
        data_agendamento = agendamento.appointment_date
        if data_agendamento.tzinfo is None:
            data_agendamento = data_agendamento.replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)
        if data_agendamento <= agora:
            raise HTTPException(
                status_code=400,
                detail="Data do agendamento deve ser no futuro"
            )
        
        # Validar tipo de consulta
        if agendamento.appointment_type == 'online':
            if not psicologo.consulta_online:
                raise HTTPException(
                    status_code=400,
                    detail="Este psicólogo não oferece consultas online"
                )
        elif agendamento.appointment_type == 'presencial':
            if not psicologo.consulta_presencial:
                raise HTTPException(
                    status_code=400,
                    detail="Este psicólogo não oferece consultas presenciais"
                )
        
        # Validar se o psicólogo trabalha neste dia e horário
        # IMPORTANTE: O frontend envia em UTC (toISOString()), mas precisamos comparar com horários locais
        # A solução mais simples: converter UTC para timezone local antes de extrair data/hora
        
        # Converter para UTC se tiver timezone
        if data_agendamento.tzinfo is not None:
            data_agendamento_utc = data_agendamento.astimezone(timezone.utc)
        else:
            data_agendamento_utc = data_agendamento.replace(tzinfo=timezone.utc)
        
        # Converter de UTC para timezone local (UTC-3 para Brasil)
        # Criar timezone local (UTC-3)
        from datetime import timezone as tz
        utc_offset = timedelta(hours=-3)
        local_tz = tz(utc_offset)
        data_agendamento_local = data_agendamento_utc.astimezone(local_tz)
        
        # Extrair data e hora no timezone local
        data_agendamento_date = data_agendamento_local.date()
        horario_agendamento = data_agendamento_local.time()
        dia_da_semana = data_agendamento_date.weekday()  # 0=Segunda, 6=Domingo
        
        print(f"DEBUG: Data agendamento (UTC): {data_agendamento_utc}")
        print(f"DEBUG: Data agendamento (Local): {data_agendamento_local}")
        print(f"DEBUG: Data: {data_agendamento_date}, Horário: {horario_agendamento}, Dia da semana: {dia_da_semana}")
        
        # Verificar disponibilidade para este dia da semana
        disponibilidades = PsychologistAvailability.listar_por_psicologo(agendamento.psychologist_id, apenas_disponiveis=True)
        disponibilidade_dia = [
            disp for disp in disponibilidades
            if disp.dia_da_semana == dia_da_semana
        ]
        
        print(f"DEBUG: Disponibilidades encontradas para dia {dia_da_semana}: {len(disponibilidade_dia)}")
        for disp in disponibilidade_dia:
            print(f"DEBUG:   - {disp.horario_inicio} até {disp.horario_fim}")
        
        if not disponibilidade_dia:
            raise HTTPException(
                status_code=400,
                detail=f"Este psicólogo não trabalha neste dia da semana. Por favor, selecione outro dia."
            )
        
        # Verificar se o horário está dentro de alguma disponibilidade
        # A lógica deve ser EXATAMENTE igual à geração de slots em disponibilidade_controller.py
        horario_valido = False
        for disp in disponibilidade_dia:
            horario_inicio = datetime.strptime(disp.horario_inicio, "%H:%M").time()
            horario_fim = datetime.strptime(disp.horario_fim, "%H:%M").time()
            
            print(f"DEBUG: Comparando horário {horario_agendamento} com disponibilidade {horario_inicio}-{horario_fim}")
            
            # Usar a mesma lógica do disponibilidade_controller.py:
            # - O horário deve ser >= horario_inicio
            # - O horário deve ser < horario_fim (não pode ser igual ou maior)
            # - O slot de 1 hora (horario_agendamento + 1h) não deve ultrapassar horario_fim
            if horario_agendamento >= horario_inicio and horario_agendamento < horario_fim:
                # Calcular próximo horário (1 hora depois) - mesma lógica do disponibilidade_controller
                data_hora_atual = datetime.combine(data_agendamento_date, horario_agendamento)
                proxima_data_hora = data_hora_atual + timedelta(hours=1)
                proximo_horario = proxima_data_hora.time()
                
                print(f"DEBUG: Próximo horário: {proximo_horario}, Horário fim: {horario_fim}")
                
                # Verificar se o próximo horário não ultrapassa o fim (mesma lógica do disponibilidade_controller)
                if proximo_horario <= horario_fim:
                    horario_valido = True
                    print(f"DEBUG: Horário válido!")
                    break
        
        if not horario_valido:
            print(f"DEBUG: Horário INVÁLIDO - não está dentro de nenhuma disponibilidade")
            raise HTTPException(
                status_code=400,
                detail="O horário selecionado não está dentro da disponibilidade do psicólogo para este dia."
            )
        
        # Verificar se o slot não está já ocupado
        agendamentos_existentes = Appointment.listar_por_psicologo(agendamento.psychologist_id)
        for apt in agendamentos_existentes:
            # Considerar apenas agendamentos confirmados como ocupando o slot
            if apt.data_agendamento.date() == data_agendamento_date and apt.status == 'confirmed':
                apt_time = apt.data_agendamento.time()
                # Verificar se há sobreposição (mesmo horário exato)
                if apt_time == horario_agendamento:
                    raise HTTPException(
                        status_code=400,
                        detail="Este horário já está ocupado. Por favor, selecione outro horário."
                    )
        
        # Criar agendamento como 'pending' - será confirmado após pagamento
        print(f"DEBUG: Criando agendamento...", file=sys.stderr, flush=True)
        agendamento_created = Appointment.criar(
            id_psicologo=agendamento.psychologist_id,
            id_usuario=usuario_atual.id,
            data_agendamento=agendamento.appointment_date,
            tipo_agendamento=agendamento.appointment_type,
            observacoes=agendamento.notes,
            status='pending'
        )
        print(f"DEBUG: Agendamento criado com ID: {agendamento_created.id}", file=sys.stderr, flush=True)
        
        # Criar notificação para o psicólogo (será atualizada após pagamento)
        try:
            print(f"DEBUG: Criando notificação para psicólogo (user_id: {psicologo.id_usuario})", file=sys.stderr, flush=True)
            Notification.criar(
                id_usuario=psicologo.id_usuario,
                titulo="Novo Agendamento Solicitado",
                mensagem=f"Você recebeu uma nova solicitação de agendamento de {usuario_atual.nome_completo}. O agendamento será confirmado após o pagamento.",
                tipo="appointment",
                id_relacionado=agendamento_created.id,
                tipo_relacionado="appointment",
                foi_lida=False
            )
            print(f"DEBUG: Notificação criada com sucesso", file=sys.stderr, flush=True)
        except Exception as notif_error:
            print(f"DEBUG: Erro ao criar notificação (não crítico): {notif_error}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
        
        # Recarregar com relacionamentos
        print(f"DEBUG: Recarregando agendamento com relacionamentos...", file=sys.stderr, flush=True)
        agendamento_created = Appointment.obter_por_id(agendamento_created.id, carregar_relacionamentos=True)
        print(f"DEBUG: Agendamento recarregado com sucesso", file=sys.stderr, flush=True)
        
        return agendamento_created
    except HTTPException:
        # Re-raise HTTP exceptions (400, 403, 404, etc.)
        raise
    except Exception as e:
        print(f"ERROR: Erro ao criar agendamento: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar agendamento: {str(e)}"
        )

@router.get("/verificar-primeira-consulta/{id_psicologo}")
def verificar_primeira_consulta(
    id_psicologo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Verificar se é a primeira consulta do usuário com o psicólogo"""
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(id_psicologo)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Verificar se o usuário já teve consultas com este psicólogo
    agendamentos = Appointment.listar_por_usuario(usuario_atual.id)
    consultas_com_psicologo = [
        apt for apt in agendamentos 
        if apt.id_psicologo == id_psicologo
    ]
    
    is_first_appointment = len(consultas_com_psicologo) == 0
    
    preco_original = psicologo.preco_consulta or 0.0
    preco_com_desconto = (preco_original * 0.7) if (is_first_appointment and preco_original > 0) else preco_original
    
    return {
        "is_first_appointment": is_first_appointment,
        "discount_percentage": 30 if is_first_appointment else 0,
        "original_price": preco_original,
        "discounted_price": preco_com_desconto
    }

@router.get("/meus-agendamentos")
def obter_meus_agendamentos(
    filtro_status: Optional[str] = None,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus agendamentos"""
    import sys
    print(f"=== DEBUG: obter_meus_agendamentos CHAMADO ===", file=sys.stderr, flush=True)
    print(f"User ID: {usuario_atual.id}", file=sys.stderr, flush=True)
    print(f"Filtro status: {filtro_status}", file=sys.stderr, flush=True)
    
    agendamentos = Appointment.listar_por_usuario(usuario_atual.id, status=filtro_status, carregar_relacionamentos=True)
    print(f"DEBUG: Total de agendamentos encontrados: {len(agendamentos)}", file=sys.stderr, flush=True)
    for i, apt in enumerate(agendamentos):
        print(f"DEBUG: Agendamento {i+1}: ID={apt.id}, Data={apt.data_agendamento}, Status={apt.status}", file=sys.stderr, flush=True)
        print(f"DEBUG:   Psychologist ID: {apt.id_psicologo}, User ID: {apt.id_usuario}", file=sys.stderr, flush=True)
    
    # Serializar manualmente para garantir que os aliases sejam usados
    try:
        serialized = [
            AppointmentResponse.model_validate(apt).model_dump(by_alias=True, mode='json')
            for apt in agendamentos
        ]
        print(f"DEBUG: Serialização concluída, {len(serialized)} agendamentos serializados", file=sys.stderr, flush=True)
        if serialized:
            print(f"DEBUG: Primeiro agendamento serializado: appointment_date={serialized[0].get('appointment_date')}", file=sys.stderr, flush=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(content=serialized)
    except Exception as e:
        print(f"ERROR: Erro ao serializar agendamentos: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Fallback: retornar sem serialização manual
        return agendamentos

@router.get("/agendamentos-psicologo", response_model=List[AppointmentResponse])
def obter_agendamentos_psicologo(
    filtro_status: Optional[str] = None,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter agendamentos do psicólogo"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar seus agendamentos"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    agendamentos = Appointment.listar_por_psicologo(psicologo.id, status=filtro_status, carregar_relacionamentos=True)
    return agendamentos

@router.get("/{id_agendamento}", response_model=AppointmentResponse)
def obter_agendamento(
    id_agendamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter agendamento por ID"""
    agendamento = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
    if not agendamento:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    # Verificar permissão
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if agendamento.user_id != usuario_atual.id and (not psicologo or agendamento.psychologist_id != psicologo.id):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para visualizar este agendamento"
        )
    
    return agendamento

@router.put("/{id_agendamento}", response_model=AppointmentResponse)
def atualizar_agendamento(
    id_agendamento: int,
    atualizacao_agendamento: AppointmentUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar agendamento"""
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    # Verificar permissão
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    pode_atualizar = (
        agendamento.user_id == usuario_atual.id or
        (psicologo and agendamento.psychologist_id == psicologo.id)
    )
    
    if not pode_atualizar:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para atualizar este agendamento"
        )
    
    # Atualizar campos
    dados_atualizacao = atualizacao_agendamento.dict(exclude_unset=True)
    agendamento.atualizar(**dados_atualizacao)
    
    # Recarregar com relacionamentos
    agendamento_db = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
    return agendamento_db

@router.delete("/{id_agendamento}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_agendamento(
    id_agendamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar agendamento"""
    import sys
    print(f"=== DEBUG: deletar_agendamento CHAMADO ===", file=sys.stderr, flush=True)
    print(f"ID Agendamento: {id_agendamento}", file=sys.stderr, flush=True)
    print(f"User ID: {usuario_atual.id}", file=sys.stderr, flush=True)
    
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento:
        print(f"DEBUG: Agendamento não encontrado", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    print(f"DEBUG: Agendamento encontrado - ID Usuário: {agendamento.id_usuario}, Status: {agendamento.status}", file=sys.stderr, flush=True)
    
    if agendamento.id_usuario != usuario_atual.id:
        print(f"DEBUG: Usuário não tem permissão - agendamento.id_usuario={agendamento.id_usuario}, usuario_atual.id={usuario_atual.id}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para cancelar este agendamento"
        )
    
    # Em vez de deletar, marcar como cancelado
    agendamento.atualizar(status='cancelled')
    print(f"DEBUG: Agendamento marcado como cancelado", file=sys.stderr, flush=True)
    
    return None

@router.post("/{id_agendamento}/confirmar")
def confirmar_agendamento(
    id_agendamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Confirmar agendamento (apenas psicólogo)"""
    import sys
    print(f"=== DEBUG: confirmar_agendamento CHAMADO ===", file=sys.stderr, flush=True)
    print(f"ID Agendamento: {id_agendamento}", file=sys.stderr, flush=True)
    print(f"User ID: {usuario_atual.id}, É psicólogo: {usuario_atual.eh_psicologo}", file=sys.stderr, flush=True)
    
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem confirmar agendamentos"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    print(f"DEBUG: Psicólogo encontrado - ID: {psicologo.id}", file=sys.stderr, flush=True)
    
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento:
        print(f"DEBUG: Agendamento não encontrado", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    print(f"DEBUG: Agendamento encontrado - ID Psicólogo: {agendamento.id_psicologo}, Status: {agendamento.status}", file=sys.stderr, flush=True)
    
    if agendamento.id_psicologo != psicologo.id:
        print(f"DEBUG: Psicólogo não tem permissão - agendamento.id_psicologo={agendamento.id_psicologo}, psicologo.id={psicologo.id}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para confirmar este agendamento"
        )
    
    agendamento.atualizar(status='confirmed')
    print(f"DEBUG: Agendamento atualizado para 'confirmed'", file=sys.stderr, flush=True)
    
    # Criar notificação para o cliente
    try:
        Notification.criar(
            id_usuario=agendamento.id_usuario,
            titulo="Agendamento Confirmado",
            mensagem=f"Seu agendamento foi confirmado pelo psicólogo.",
            tipo="appointment",
            id_relacionado=agendamento.id,
            tipo_relacionado="appointment",
            foi_lida=False
        )
        print(f"DEBUG: Notificação criada com sucesso", file=sys.stderr, flush=True)
    except Exception as notif_error:
        print(f"DEBUG: Erro ao criar notificação (não crítico): {notif_error}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    # Recarregar com relacionamentos
    agendamento = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
    # Serializar manualmente para garantir que os aliases sejam usados
    try:
        serialized = AppointmentResponse.model_validate(agendamento).model_dump(by_alias=True, mode='json')
        print(f"DEBUG: Serialização concluída", file=sys.stderr, flush=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(content=serialized)
    except Exception as e:
        print(f"ERROR: Erro ao serializar agendamento: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Fallback: retornar sem serialização manual
        return agendamento

@router.post("/{id_agendamento}/recusar", response_model=AppointmentResponse)
def recusar_agendamento(
    id_agendamento: int,
    motivo_recusa: str = Query(..., description="Motivo da recusa"),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Recusar agendamento (apenas psicólogo)"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem recusar agendamentos"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento or agendamento.psychologist_id != psicologo.id:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    agendamento.atualizar(status='rejected', rejection_reason=motivo_recusa)
    
    # Criar notificação para o cliente
    Notification.criar(
        id_usuario=agendamento.id_usuario,
        titulo="Agendamento Recusado",
        mensagem=f"Seu agendamento foi recusado. Motivo: {motivo_recusa}",
        tipo="appointment",
        id_relacionado=agendamento.id,
        tipo_relacionado="appointment",
        foi_lida=False
    )
    
    # Recarregar com relacionamentos
    agendamento = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
    return agendamento


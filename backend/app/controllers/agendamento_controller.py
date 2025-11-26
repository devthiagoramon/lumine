"""
Appointment Controller - Endpoints de agendamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone
from app import auth
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.agendamento import Appointment
from app.models.notificacao import Notification

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def criar_agendamento(
    agendamento: AppointmentCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar agendamento"""
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(agendamento.psychologist_id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
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
        if not psicologo.online_consultation:
            raise HTTPException(
                status_code=400,
                detail="Este psicólogo não oferece consultas online"
            )
    elif agendamento.appointment_type == 'presencial':
        if not psicologo.in_person_consultation:
            raise HTTPException(
                status_code=400,
                detail="Este psicólogo não oferece consultas presenciais"
            )
    
    # Criar agendamento
    agendamento_created = Appointment.criar(
        psychologist_id=agendamento.psychologist_id,
        user_id=usuario_atual.id,
        appointment_date=agendamento.appointment_date,
        appointment_type=agendamento.appointment_type,
        notes=agendamento.notes,
        status='pending'
    )
    
    # Criar notificação para o psicólogo
    Notification.criar(
        user_id=psicologo.user_id,
        title="Novo Agendamento Solicitado",
        message=f"Você recebeu uma nova solicitação de agendamento de {usuario_atual.nome_completo}.",
        type="appointment",
        related_id=agendamento_created.id,
        related_type="appointment",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    agendamento_created = Appointment.obter_por_id(agendamento_created.id, carregar_relacionamentos=True)
    
    return agendamento_created

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
        if apt.psychologist_id == id_psicologo
    ]
    
    is_first_appointment = len(consultas_com_psicologo) == 0
    
    return {
        "is_first_appointment": is_first_appointment,
        "discount_percentage": 30 if is_first_appointment else 0,
        "original_price": psicologo.consultation_price or 0.0,
        "discounted_price": (psicologo.consultation_price * 0.7) if (is_first_appointment and psicologo.consultation_price) else (psicologo.consultation_price or 0.0)
    }

@router.get("/meus-agendamentos", response_model=List[AppointmentResponse])
def obter_meus_agendamentos(
    filtro_status: Optional[str] = None,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus agendamentos"""
    agendamentos = Appointment.listar_por_usuario(usuario_atual.id, status=filtro_status)
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
    
    agendamentos = Appointment.listar_por_psicologo(psicologo.id, status=filtro_status)
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
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento or agendamento.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    agendamento.deletar()
    
    return None

@router.post("/{id_agendamento}/confirmar", response_model=AppointmentResponse)
def confirmar_agendamento(
    id_agendamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Confirmar agendamento (apenas psicólogo)"""
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
    
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento or agendamento.psychologist_id != psicologo.id:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    agendamento.atualizar(status='confirmed')
    
    # Criar notificação para o cliente
    Notification.criar(
        user_id=agendamento.user_id,
        title="Agendamento Confirmado",
        message=f"Seu agendamento foi confirmado pelo psicólogo.",
        type="appointment",
        related_id=agendamento.id,
        related_type="appointment",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    agendamento = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
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
        user_id=agendamento.user_id,
        title="Agendamento Recusado",
        message=f"Seu agendamento foi recusado. Motivo: {motivo_recusa}",
        type="appointment",
        related_id=agendamento.id,
        related_type="appointment",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    agendamento = Appointment.obter_por_id(id_agendamento, carregar_relacionamentos=True)
    
    return agendamento


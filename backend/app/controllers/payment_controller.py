"""
Payment Controller - Endpoints de pagamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app import auth
from app.schemas import PaymentCreate, PaymentResponse
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.notification import Notification
import uuid
import random
import time

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def criar_pagamento(
    pagamento: PaymentCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar pagamento"""
    # Verificar se agendamento existe
    agendamento = Appointment.obter_por_id(pagamento.appointment_id)
    
    if not agendamento:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    # Verificar se agendamento pertence ao usuário
    if agendamento.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode pagar seus próprios agendamentos"
        )
    
    # Verificar se agendamento está confirmado (conforme diagrama de sequência)
    if agendamento.status != 'confirmed':
        raise HTTPException(
            status_code=400,
            detail="Agendamento deve ser confirmado pelo psicólogo antes do pagamento"
        )
    
    # Verificar se já foi pago
    pagamento_existente = Payment.obter_por_agendamento(pagamento.appointment_id)
    
    if pagamento_existente and pagamento_existente.status == 'paid':
        raise HTTPException(
            status_code=400,
            detail="Agendamento já foi pago"
        )
    
    # Obter valor do psicólogo
    psicologo = Psychologist.obter_por_id(agendamento.psychologist_id)
    
    if not psicologo or not psicologo.consultation_price:
        raise HTTPException(
            status_code=400,
            detail="Preço da consulta do psicólogo não definido"
        )
    
    # Verificar se é primeira consulta para aplicar desconto de 30%
    agendamentos_anteriores = Appointment.listar_por_usuario(usuario_atual.id)
    consultas_com_psicologo = [
        agendamento_anterior for agendamento_anterior in agendamentos_anteriores 
        if agendamento_anterior.psychologist_id == agendamento.psychologist_id and agendamento_anterior.id != agendamento.id
    ]
    
    é_primeira_consulta = len(consultas_com_psicologo) == 0
    
    # Aplicar desconto de 30% se for primeira consulta
    if é_primeira_consulta:
        valor = psicologo.consultation_price * 0.7  # 30% de desconto
    else:
        valor = psicologo.consultation_price
    
    # Processar pagamento mockado
    time.sleep(0.5)  # Simular delay
    sucesso = random.random() > 0.05  # 95% de sucesso
    
    if sucesso:
        status_pagamento = "paid"
        id_pagamento = f"PAY-{uuid.uuid4().hex[:16].upper()}"
        id_transacao = f"TXN-{uuid.uuid4().hex[:16].upper()}"
    else:
        status_pagamento = "failed"
        id_pagamento = f"PAY-{uuid.uuid4().hex[:16].upper()}"
        id_transacao = None
    
    # Criar registro de pagamento
    pagamento_db = Payment.criar(
        appointment_id=pagamento.appointment_id,
        user_id=usuario_atual.id,
        amount=valor,
        payment_method=pagamento.payment_method,
        status=status_pagamento,
        payment_id=id_pagamento,
        transaction_id=id_transacao
    )
    
    # Atualizar status do agendamento
    agendamento.atualizar(payment_status=status_pagamento, payment_id=id_pagamento)
    
    if status_pagamento == "paid":
        # Processar pagamento e atualizar saldo do psicólogo (80% para o psicólogo, 20% para a plataforma)
        parte_psicologo = valor * 0.80
        psicologo.atualizar(balance=(psicologo.balance or 0.0) + parte_psicologo)
        
        # Criar notificação para o psicólogo
        Notification.criar(
            user_id=psicologo.user_id,
            title="Novo Pagamento Recebido",
            message=f"Você recebeu R$ {parte_psicologo:.2f} de uma consulta.",
            type="payment",
            related_id=pagamento_db.id,
            related_type="payment",
            is_read=False
        )
        
        # Criar notificação para o cliente
        Notification.criar(
            user_id=agendamento.user_id,
            title="Pagamento Confirmado",
            message="Seu pagamento foi processado com sucesso.",
            type="payment",
            related_id=pagamento_db.id,
            related_type="payment",
            is_read=False
        )
    
    return pagamento_db

@router.get("/agendamento/{id_agendamento}", response_model=PaymentResponse)
def obter_pagamento_por_agendamento(
    id_agendamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter pagamento por id_agendamento"""
    pagamento = Payment.obter_por_agendamento(id_agendamento)
    
    if not pagamento:
        raise HTTPException(
            status_code=404,
            detail="Pagamento não encontrado"
        )
    
    # Verificar permissão
    agendamento = Appointment.obter_por_id(id_agendamento)
    
    if not agendamento:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    if agendamento.user_id != usuario_atual.id:
        # Verificar se é psicólogo do agendamento
        psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
        
        if not psicologo or agendamento.psychologist_id != psicologo.id:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para visualizar este pagamento"
            )
    
    return pagamento

@router.get("/meus-pagamentos", response_model=List[PaymentResponse])
def obter_meus_pagamentos(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus pagamentos"""
    pagamentos = Payment.listar_por_usuario(usuario_atual.id)
    return pagamentos

@router.post("/{id_pagamento}/reembolsar", response_model=PaymentResponse)
def reembolsar_pagamento(
    id_pagamento: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Reembolsar pagamento"""
    pagamento = Payment.obter_por_id(id_pagamento)
    
    if not pagamento or pagamento.user_id != usuario_atual.id or pagamento.status != "paid":
        raise HTTPException(
            status_code=404,
            detail="Pagamento não encontrado ou não pode ser reembolsado"
        )
    
    transaction_id_refund = f"{pagamento.transaction_id}-REFUND" if pagamento.transaction_id else "REFUND"
    pagamento.atualizar(status="refunded", transaction_id=transaction_id_refund)
    
    # Atualizar agendamento
    agendamento = Appointment.obter_por_id(pagamento.appointment_id)
    
    if agendamento:
        agendamento.atualizar(payment_status="refunded", status="cancelled")
    
    return pagamento

@router.get("/historico-financeiro", response_model=List[PaymentResponse])
def obter_historico_financeiro(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter histórico financeiro (para psicólogos)"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar histórico financeiro"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    # Obter agendamentos do psicólogo
    agendamentos = Appointment.listar_por_psicologo(psicologo.id)
    
    ids_agendamentos = [ag.id for ag in agendamentos]
    
    # Filtrar pagamentos pagos dos agendamentos do psicólogo
    pagamentos = Payment.listar_por_usuario(usuario_atual.id)
    pagamentos = [p for p in pagamentos if p.appointment_id in ids_agendamentos and p.status == 'paid']
    
    return pagamentos

@router.get("/saldo")
def obter_saldo(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter saldo disponível (para psicólogos)"""
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem visualizar saldo"
        )
    
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    return {
        "balance": psicologo.balance or 0.0,
        "psychologist_id": psicologo.id
    }


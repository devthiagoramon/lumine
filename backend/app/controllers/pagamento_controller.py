"""
Payment Controller - Endpoints de pagamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app import auth
from app.schemas import PaymentCreate, PaymentResponse
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.agendamento import Appointment
from app.models.pagamento import Payment
from app.models.notificacao import Notification
import uuid
import random
import time

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_pagamento(
    pagamento: PaymentCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar pagamento"""
    import sys
    print(f"=== DEBUG: criar_pagamento CHAMADO ===", file=sys.stderr, flush=True)
    print(f"Appointment ID: {pagamento.appointment_id}", file=sys.stderr, flush=True)
    print(f"Payment Method: {pagamento.payment_method}", file=sys.stderr, flush=True)
    print(f"User ID: {usuario_atual.id}", file=sys.stderr, flush=True)
    
    # Verificar se agendamento existe
    agendamento = Appointment.obter_por_id(pagamento.appointment_id)
    
    if not agendamento:
        print(f"DEBUG: Agendamento não encontrado", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    
    print(f"DEBUG: Agendamento encontrado - Status: {agendamento.status}, ID Usuário: {agendamento.id_usuario}", file=sys.stderr, flush=True)
    
    # Verificar se agendamento pertence ao usuário
    if agendamento.id_usuario != usuario_atual.id:
        print(f"DEBUG: Usuário não tem permissão - agendamento.id_usuario={agendamento.id_usuario}, usuario_atual.id={usuario_atual.id}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=403,
            detail="Você só pode pagar seus próprios agendamentos"
        )
    
    # Verificar se agendamento está pendente (será confirmado após pagamento)
    if agendamento.status not in ['pending', 'confirmed']:
        print(f"DEBUG: Agendamento não pode ser pago - status={agendamento.status}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=400,
            detail="Apenas agendamentos pendentes ou confirmados podem ser pagos"
        )
    
    # Verificar se já foi pago
    pagamento_existente = Payment.obter_por_agendamento(pagamento.appointment_id)
    
    if pagamento_existente and pagamento_existente.status == 'paid':
        print(f"DEBUG: Agendamento já foi pago", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=400,
            detail="Agendamento já foi pago"
        )
    
    # Obter valor do psicólogo
    psicologo = Psychologist.obter_por_id(agendamento.id_psicologo)
    
    if not psicologo:
        print(f"DEBUG: Psicólogo não encontrado", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    print(f"DEBUG: Psicólogo encontrado - Preço: {psicologo.preco_consulta}", file=sys.stderr, flush=True)
    
    if not psicologo.preco_consulta or psicologo.preco_consulta <= 0:
        print(f"DEBUG: Preço da consulta inválido - preco_consulta={psicologo.preco_consulta}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=400,
            detail="Preço da consulta do psicólogo não definido"
        )
    
    # Verificar se é primeira consulta para aplicar desconto de 30%
    agendamentos_anteriores = Appointment.listar_por_usuario(usuario_atual.id)
    consultas_com_psicologo = [
        agendamento_anterior for agendamento_anterior in agendamentos_anteriores 
        if agendamento_anterior.id_psicologo == agendamento.id_psicologo and agendamento_anterior.id != agendamento.id
    ]
    
    é_primeira_consulta = len(consultas_com_psicologo) == 0
    
    # Aplicar desconto de 30% se for primeira consulta
    if é_primeira_consulta:
        valor = psicologo.preco_consulta * 0.7  # 30% de desconto
    else:
        valor = psicologo.preco_consulta
    
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
    pagamento_created = Payment.criar(
        id_agendamento=pagamento.appointment_id,
        id_usuario=usuario_atual.id,
        valor=valor,
        metodo_pagamento=pagamento.payment_method,
        status=status_pagamento,
        id_pagamento=id_pagamento,
        id_transacao=id_transacao
    )
    
    # Atualizar status do agendamento (usar nome do campo do modelo)
    print(f"DEBUG: Atualizando agendamento {agendamento.id} - status_pagamento: {status_pagamento}, id_pagamento: {id_pagamento}", file=sys.stderr, flush=True)
    agendamento.atualizar(status_pagamento=status_pagamento, id_pagamento=id_pagamento)
    
    # Recarregar agendamento do banco para garantir que temos a versão mais recente
    agendamento = Appointment.obter_por_id(agendamento.id)
    print(f"DEBUG: Agendamento recarregado - status: {agendamento.status}, status_pagamento: {agendamento.status_pagamento}", file=sys.stderr, flush=True)
    
    if status_pagamento == "paid":
        # Confirmar agendamento após pagamento bem-sucedido
        if agendamento.status == 'pending':
            agendamento.atualizar(status='confirmed')
            # Recarregar novamente após confirmar
            agendamento = Appointment.obter_por_id(agendamento.id)
            print(f"DEBUG: Agendamento confirmado após pagamento - ID: {agendamento.id}, status: {agendamento.status}, status_pagamento: {agendamento.status_pagamento}", file=sys.stderr, flush=True)
            
            # Atualizar notificação do psicólogo sobre confirmação
            try:
                Notification.criar(
                    id_usuario=psicologo.id_usuario,
                    titulo="Agendamento Confirmado",
                    mensagem=f"O agendamento com {usuario_atual.nome_completo} foi confirmado após o pagamento.",
                    tipo="appointment",
                    id_relacionado=agendamento.id,
                    tipo_relacionado="appointment",
                    foi_lida=False
                )
            except Exception as e:
                print(f"DEBUG: Erro ao criar notificação de confirmação (não crítico): {e}", file=sys.stderr, flush=True)
        
        # Processar pagamento e atualizar saldo do psicólogo (80% para o psicólogo, 20% para a plataforma)
        parte_psicologo = valor * 0.80
        saldo_atual = psicologo.saldo or 0.0
        psicologo.atualizar(saldo=saldo_atual + parte_psicologo)
        print(f"DEBUG: Saldo atualizado - Antes: {saldo_atual}, Depois: {saldo_atual + parte_psicologo}", file=sys.stderr, flush=True)
        
        # Criar notificação para o psicólogo sobre pagamento
        try:
            Notification.criar(
                id_usuario=psicologo.id_usuario,
                titulo="Novo Pagamento Recebido",
                mensagem=f"Você recebeu R$ {parte_psicologo:.2f} de uma consulta.",
                tipo="payment",
                id_relacionado=pagamento_created.id,
                tipo_relacionado="payment",
                foi_lida=False
            )
        except Exception as e:
            print(f"DEBUG: Erro ao criar notificação para psicólogo (não crítico): {e}", file=sys.stderr, flush=True)
        
        # Criar notificação para o cliente
        try:
            Notification.criar(
                id_usuario=agendamento.id_usuario,
                titulo="Pagamento Confirmado",
                mensagem="Seu pagamento foi processado com sucesso.",
                tipo="payment",
                id_relacionado=pagamento_created.id,
                tipo_relacionado="payment",
                foi_lida=False
            )
        except Exception as e:
            print(f"DEBUG: Erro ao criar notificação para cliente (não crítico): {e}", file=sys.stderr, flush=True)
    
    # Serializar manualmente para garantir que os aliases sejam usados
    try:
        from app.schemas import PaymentResponse
        serialized = PaymentResponse.model_validate(pagamento_created).model_dump(by_alias=True, mode='json')
        print(f"DEBUG: Pagamento serializado com sucesso", file=sys.stderr, flush=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(content=serialized, status_code=201)
    except Exception as e:
        print(f"ERROR: Erro ao serializar pagamento: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Fallback: retornar sem serialização manual
        return pagamento_created
    
    return pagamento_created

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
    
    if agendamento.id_usuario != usuario_atual.id:
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
    
    if not pagamento or pagamento.id_usuario != usuario_atual.id or pagamento.status != "paid":
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


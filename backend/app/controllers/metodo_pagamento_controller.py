"""
Payment Method Controller - Endpoints para gerenciar métodos de pagamento salvos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import auth
from app.schemas.metodo_pagamento import (
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse
)
from app.models.usuario import User
from app.models.metodo_pagamento import PaymentMethod
import re
import sys

router = APIRouter()

def detect_card_brand(card_number: str) -> str:
    """Detectar a bandeira do cartão baseado no número"""
    # Remover espaços
    card_number = re.sub(r'\s+', '', card_number)
    
    # Visa: começa com 4
    if card_number.startswith('4'):
        return 'visa'
    # Mastercard: começa com 5 ou 2
    elif card_number.startswith('5') or card_number.startswith('2'):
        return 'mastercard'
    # Amex: começa com 34 ou 37
    elif card_number.startswith('34') or card_number.startswith('37'):
        return 'amex'
    # Elo: começa com vários prefixos
    elif any(card_number.startswith(prefix) for prefix in ['401178', '401179', '431274', '438935', '451416', '457393', '457631', '457632', '504175', '627780', '636297', '636368', '636369']):
        return 'elo'
    else:
        return 'unknown'

def parse_expiry(expiry: str) -> tuple:
    """Converter MM/YY em (month, year)"""
    month, year = expiry.split('/')
    # Converter YY para YYYY
    full_year = f"20{year}" if len(year) == 2 else year
    return month, full_year

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_metodo_pagamento(
    metodo: PaymentMethodCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar novo método de pagamento"""
    try:
        print(f"=== DEBUG: criar_metodo_pagamento CHAMADO ===", file=sys.stderr, flush=True)
        print(f"Card Type: {metodo.card_type}", file=sys.stderr, flush=True)
        print(f"Card Number: {metodo.card_number[:4]}...{metodo.card_number[-4:]}", file=sys.stderr, flush=True)
        print(f"Card Holder: {metodo.card_holder}", file=sys.stderr, flush=True)
        print(f"Card Expiry: {metodo.card_expiry}", file=sys.stderr, flush=True)
        print(f"Card CVV: {'*' * len(metodo.card_cvv)}", file=sys.stderr, flush=True)
        print(f"Is Default: {metodo.is_default}", file=sys.stderr, flush=True)
        
        # Detectar bandeira do cartão
        card_brand = detect_card_brand(metodo.card_number)
        
        # Extrair últimos 4 dígitos
        last_four = metodo.card_number[-4:]
        
        # Parse da data de validade
        expiry_month, expiry_year = parse_expiry(metodo.card_expiry)
        
        # Criar método de pagamento
        # Mapear campos do schema para o modelo (português)
        metodo_created = PaymentMethod.criar(
            id_usuario=usuario_atual.id,
            tipo_cartao=metodo.card_type,
            bandeira=card_brand,
            ultimos_quatro_digitos=last_four,
            portador=metodo.card_holder.upper(),
            mes_validade=expiry_month,
            ano_validade=expiry_year,
            eh_padrao=metodo.is_default
        )
        
        # Serializar manualmente para garantir campos corretos
        try:
            from app.schemas.metodo_pagamento import PaymentMethodResponse
            metodo_dict = PaymentMethodResponse.model_validate(metodo_created).model_dump(by_alias=True, mode='json')
            from fastapi.responses import JSONResponse
            print(f"DEBUG: Método criado com sucesso - ID: {metodo_created.id}", file=sys.stderr, flush=True)
            return JSONResponse(content=metodo_dict, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            print(f"ERROR: Erro ao serializar método de pagamento: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            return metodo_created
    except Exception as e:
        import traceback
        print(f"ERROR: Erro ao criar método de pagamento: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar método de pagamento: {str(e)}"
        )

@router.get("/", response_model=List[PaymentMethodResponse])
def listar_metodos_pagamento(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Listar métodos de pagamento do usuário"""
    metodos = PaymentMethod.listar_por_usuario(usuario_atual.id)
    # Serializar manualmente
    try:
        from app.schemas.metodo_pagamento import PaymentMethodResponse
        metodos_dict = [PaymentMethodResponse.model_validate(m).model_dump(by_alias=True, mode='json') for m in metodos]
        from fastapi.responses import JSONResponse
        return JSONResponse(content=metodos_dict)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar métodos de pagamento: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return metodos

@router.get("/{id_metodo}", response_model=PaymentMethodResponse)
def obter_metodo_pagamento(
    id_metodo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter método de pagamento por ID"""
    metodo = PaymentMethod.obter_por_id(id_metodo)
    
    if not metodo:
        raise HTTPException(
            status_code=404,
            detail="Método de pagamento não encontrado"
        )
    
    if metodo.id_usuario != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar este método de pagamento"
        )
    
    # Serializar manualmente
    try:
        from app.schemas.metodo_pagamento import PaymentMethodResponse
        metodo_dict = PaymentMethodResponse.model_validate(metodo).model_dump(by_alias=True, mode='json')
        from fastapi.responses import JSONResponse
        return JSONResponse(content=metodo_dict)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar método de pagamento: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return metodo

@router.put("/{id_metodo}", response_model=PaymentMethodResponse)
def atualizar_metodo_pagamento(
    id_metodo: int,
    metodo_update: PaymentMethodUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar método de pagamento"""
    metodo = PaymentMethod.obter_por_id(id_metodo)
    
    if not metodo:
        raise HTTPException(
            status_code=404,
            detail="Método de pagamento não encontrado"
        )
    
    if metodo.id_usuario != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para atualizar este método de pagamento"
        )
    
    # Preparar dados para atualização (mapear para nomes do modelo)
    update_data = {}
    
    if metodo_update.card_holder is not None:
        update_data['portador'] = metodo_update.card_holder.upper()
    
    if metodo_update.card_expiry is not None:
        expiry_month, expiry_year = parse_expiry(metodo_update.card_expiry)
        update_data['mes_validade'] = expiry_month
        update_data['ano_validade'] = expiry_year
    
    if metodo_update.is_default is not None:
        update_data['eh_padrao'] = metodo_update.is_default
    
    metodo_atualizado = metodo.atualizar(**update_data)
    
    # Recarregar método
    metodo_atualizado = PaymentMethod.obter_por_id(id_metodo)
    
    # Serializar manualmente
    try:
        from app.schemas.metodo_pagamento import PaymentMethodResponse
        metodo_dict = PaymentMethodResponse.model_validate(metodo_atualizado).model_dump(by_alias=True, mode='json')
        from fastapi.responses import JSONResponse
        return JSONResponse(content=metodo_dict)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar método de pagamento atualizado: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return metodo_atualizado

@router.post("/{id_metodo}/definir-padrao", response_model=PaymentMethodResponse)
def definir_metodo_padrao(
    id_metodo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Definir método de pagamento como padrão"""
    metodo = PaymentMethod.obter_por_id(id_metodo)
    
    if not metodo:
        raise HTTPException(
            status_code=404,
            detail="Método de pagamento não encontrado"
        )
    
    if metodo.id_usuario != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para definir este método como padrão"
        )
    
    metodo_atualizado = metodo.atualizar(eh_padrao=True)
    
    # Recarregar método
    metodo_atualizado = PaymentMethod.obter_por_id(id_metodo)
    
    # Serializar manualmente
    try:
        from app.schemas.metodo_pagamento import PaymentMethodResponse
        metodo_dict = PaymentMethodResponse.model_validate(metodo_atualizado).model_dump(by_alias=True, mode='json')
        from fastapi.responses import JSONResponse
        return JSONResponse(content=metodo_dict)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar método de pagamento: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return metodo_atualizado

@router.delete("/{id_metodo}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_metodo_pagamento(
    id_metodo: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar método de pagamento"""
    metodo = PaymentMethod.obter_por_id(id_metodo)
    
    if not metodo:
        raise HTTPException(
            status_code=404,
            detail="Método de pagamento não encontrado"
        )
    
    if metodo.id_usuario != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para deletar este método de pagamento"
        )
    
    metodo.deletar()
    
    return None


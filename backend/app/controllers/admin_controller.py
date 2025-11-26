"""
Admin Controller - Endpoints administrativos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from app import auth
from app.schemas import (
    PsychologistResponse, ForumPostResponse, PsychologistPreRegistrationResponse
)
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.post_forum import ForumPost
from app.models.pre_registro_psicologo import PsychologistPreRegistration
from app.models.notificacao import Notification
from app.models.comentario_forum import ForumComment
from app.models.especialidade import Specialty
from app.models.tratamento import Approach
import json

router = APIRouter()

# ========== ROTAS PARA VALIDAÇÃO DE PSICÓLOGOS ==========

@router.get("/psychologists/pending")
def listar_psicologos_pendentes(
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Lista todos os psicólogos pendentes de validação"""
    psychologists = Psychologist.listar_pendentes()
    
    # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
    try:
        # Pydantic v2
        serialized = [
            PsychologistResponse.model_validate(p).model_dump(by_alias=False, mode='json')
            for p in psychologists
        ]
    except AttributeError:
        # Pydantic v1 fallback
        serialized = [
            PsychologistResponse.from_orm(p).dict(by_alias=False)
            for p in psychologists
        ]
    
    return JSONResponse(content=serialized)

@router.put("/psychologists/{id_psicologo}/verify")
def verificar_psicologo(
    id_psicologo: int,
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Valida o cadastro de um psicólogo"""
    try:
        psychologist = Psychologist.obter_por_id(id_psicologo, carregar_relacionamentos=True)
        
        if not psychologist:
            raise HTTPException(
                status_code=404,
                detail="Psicólogo não encontrado"
            )
        
        # Guardar user_id antes de atualizar (caso a sessão seja fechada)
        user_id = psychologist.id_usuario
        
        psychologist.atualizar(esta_verificado=True)
        
        # Criar notificação para o psicólogo
        try:
            Notification.criar(
                user_id=user_id,
                title="Cadastro Verificado",
                message="Seu cadastro foi verificado e aprovado pela administração.",
                type="system",
                related_id=id_psicologo,
                related_type="psychologist",
                is_read=False
            )
        except Exception as e:
            # Log do erro mas não falhar a operação
            print(f"Erro ao criar notificação: {e}")
        
        # Recarregar com relacionamentos
        psychologist = Psychologist.obter_por_id(id_psicologo, carregar_relacionamentos=True)
        
        # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
        try:
            # Pydantic v2
            response_obj = PsychologistResponse.model_validate(psychologist)
            serialized = response_obj.model_dump(by_alias=False, mode='json')
        except AttributeError:
            # Pydantic v1 fallback
            response_obj = PsychologistResponse.from_orm(psychologist)
            serialized = response_obj.dict(by_alias=False)
        
        return JSONResponse(content=serialized)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar psicólogo: {str(e)}"
        )

@router.put("/psychologists/{id_psicologo}/unverify")
def desverificar_psicologo(
    id_psicologo: int,
    motivo: str = Query(..., min_length=5, description="Motivo da desvalidação"),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Remove a validação de um psicólogo"""
    try:
        psychologist = Psychologist.obter_por_id(id_psicologo, carregar_relacionamentos=True)
        
        if not psychologist:
            raise HTTPException(
                status_code=404,
                detail="Psicólogo não encontrado"
            )
        
        # Guardar user_id antes de atualizar (caso a sessão seja fechada)
        user_id = psychologist.id_usuario
        
        # Verificar se é uma rejeição (nunca foi verificado) ou remoção de validação (já foi verificado antes)
        is_rejection = not psychologist.esta_verificado
        
        # Atualizar campos
        update_data = {'esta_verificado': False}
        if is_rejection:
            # Se o campo rejeitado existir, marcar como rejeitado
            update_data['rejeitado'] = True
        
        psychologist.atualizar(**update_data)
        
        # Criar notificação para o psicólogo
        try:
            Notification.criar(
                user_id=user_id,
                title="Cadastro Desverificado",
                message=f"Seu cadastro foi desverificado pela administração. Motivo: {motivo}",
                type="system",
                related_id=id_psicologo,
                related_type="psychologist",
                is_read=False
            )
        except Exception as e:
            # Log do erro mas não falhar a operação
            print(f"Erro ao criar notificação: {e}")
        
        # Recarregar com relacionamentos
        psychologist = Psychologist.obter_por_id(id_psicologo, carregar_relacionamentos=True)
        
        # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
        try:
            # Pydantic v2
            response_obj = PsychologistResponse.model_validate(psychologist)
            serialized = response_obj.model_dump(by_alias=False, mode='json')
        except AttributeError:
            # Pydantic v1 fallback
            response_obj = PsychologistResponse.from_orm(psychologist)
            serialized = response_obj.dict(by_alias=False)
        
        return JSONResponse(content=serialized)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao desverificar psicólogo: {str(e)}"
        )

# ========== ROTAS PARA GERENCIAMENTO DE FÓRUNS ==========

@router.delete("/forum/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_post_como_admin(
    id_post: int,
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Deletar post como administrador"""
    post = ForumPost.obter_por_id(id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post não encontrado"
        )
    
    user_id_post = post.user_id
    post.deletar()
    
    # Criar notificação para o autor
    Notification.criar(
        user_id=user_id_post,
        title="Post Removido",
        message="Seu post foi removido pela administração.",
        type="system",
        related_id=id_post,
        related_type="forum_post",
        is_read=False
    )
    
    return None

@router.get("/forum/posts", response_model=List[ForumPostResponse])
def listar_todos_posts(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Listar todos os posts (admin)"""
    posts = ForumPost.listar(pagina=pagina, tamanho_pagina=tamanho_pagina)
    return posts

# ========== ROTAS PARA PRÉ-CADASTRO ==========

@router.get("/pre-registrations/pending", response_model=List[PsychologistPreRegistrationResponse])
def listar_pre_cadastros_pendentes(
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Listar pré-cadastros pendentes"""
    pre_registrations = PsychologistPreRegistration.listar_pendentes()
    return pre_registrations

@router.post("/pre-registrations/{id_pre_cadastro}/approve", response_model=PsychologistResponse)
def aprovar_pre_cadastro(
    id_pre_cadastro: int,
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Aprovar pré-cadastro e criar perfil de psicólogo"""
    pre_reg = PsychologistPreRegistration.obter_por_id(id_pre_cadastro)
    
    if not pre_reg or pre_reg.status != 'pending':
        raise HTTPException(
            status_code=404,
            detail="Pré-cadastro não encontrado ou já processado"
        )
    
    # Parse specialty_ids e approach_ids
    specialty_ids = json.loads(pre_reg.specialty_ids) if pre_reg.specialty_ids else []
    approach_ids = json.loads(pre_reg.approach_ids) if pre_reg.approach_ids else []
    
    # Criar perfil de psicólogo com relacionamentos
    psychologist = Psychologist.criar_com_relacionamentos(
        user_id=pre_reg.user_id,
        crp=pre_reg.crp,
        bio=pre_reg.bio,
        experience_years=pre_reg.experience_years,
        consultation_price=pre_reg.consultation_price,
        online_consultation=pre_reg.online_consultation,
        in_person_consultation=pre_reg.in_person_consultation,
        address=pre_reg.address,
        city=pre_reg.city,
        state=pre_reg.state,
        zip_code=pre_reg.zip_code,
        is_verified=False,
        specialty_ids=specialty_ids,
        approach_ids=approach_ids
    )
    
    # Atualizar status do pré-cadastro
    pre_reg.atualizar(status='approved')
    
    # Criar notificação para o usuário
    Notification.criar(
        user_id=psychologist.user_id,
        title="Pré-cadastro Aprovado",
        message="Seu pré-cadastro foi aprovado e seu perfil de psicólogo foi criado.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    psychologist = Psychologist.obter_por_id(psychologist.id, carregar_relacionamentos=True)
    
    return psychologist

@router.post("/pre-registrations/{id_pre_cadastro}/reject")
def rejeitar_pre_cadastro(
    id_pre_cadastro: int,
    motivo_rejeicao: str,
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Rejeitar pré-cadastro"""
    pre_registration = PsychologistPreRegistration.obter_por_id(id_pre_cadastro)
    
    if not pre_registration:
        raise HTTPException(
            status_code=404,
            detail="Pré-cadastro não encontrado"
        )
    
    pre_registration.atualizar(status='rejected', rejection_reason=motivo_rejeicao)
    
    # Criar notificação para o usuário
    Notification.criar(
        user_id=pre_registration.user_id,
        title="Pré-cadastro Rejeitado",
        message=f"Seu pré-cadastro foi rejeitado. Motivo: {motivo_rejeicao}",
        type="system",
        related_id=id_pre_cadastro,
        related_type="pre_registration",
        is_read=False
    )
    
    return {"message": "Pré-cadastro rejeitado", "pre_registration": pre_registration}


"""
Admin Controller - Endpoints administrativos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistResponse, ForumPostResponse, PsychologistPreRegistrationResponse
)
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.forum_post import ForumPost
from app.models.psychologist_pre_registration import PsychologistPreRegistration
from app.models.notification import Notification
from app.models.forum_comment import ForumComment
from app.models.specialty import Specialty
from app.models.approach import Approach
import json

router = APIRouter()

# ========== ROTAS PARA VALIDAÇÃO DE PSICÓLOGOS ==========

@router.get("/psychologists/pending", response_model=List[PsychologistResponse])
def listar_psicologos_pendentes(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Lista todos os psicólogos pendentes de validação"""
    psychologists = Psychologist.listar_pendentes(db)
    return psychologists

@router.put("/psychologists/{id_psicologo}/verify", response_model=PsychologistResponse)
def verificar_psicologo(
    id_psicologo: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Valida o cadastro de um psicólogo"""
    psychologist = Psychologist.obter_por_id(db, id_psicologo, carregar_relacionamentos=True)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.atualizar(db, is_verified=True)
    
    # Criar notificação para o psicólogo
    Notification.criar(
        db,
        user_id=psychologist.user_id,
        title="Cadastro Verificado",
        message="Seu cadastro foi verificado e aprovado pela administração.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    psychologist = Psychologist.obter_por_id(db, id_psicologo, carregar_relacionamentos=True)
    
    return psychologist

@router.put("/psychologists/{id_psicologo}/unverify", response_model=PsychologistResponse)
def desverificar_psicologo(
    id_psicologo: int,
    motivo: str = Query(..., min_length=5, description="Motivo da desvalidação"),
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Remove a validação de um psicólogo"""
    psychologist = Psychologist.obter_por_id(db, id_psicologo, carregar_relacionamentos=True)
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.atualizar(db, is_verified=False)
    
    # Criar notificação para o psicólogo
    Notification.criar(
        db,
        user_id=psychologist.user_id,
        title="Cadastro Desverificado",
        message=f"Seu cadastro foi desverificado pela administração. Motivo: {motivo}",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    psychologist = Psychologist.obter_por_id(db, id_psicologo, carregar_relacionamentos=True)
    
    return psychologist

# ========== ROTAS PARA GERENCIAMENTO DE FÓRUNS ==========

@router.delete("/forum/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_post_como_admin(
    id_post: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Deletar post como administrador"""
    post = ForumPost.obter_por_id(db, id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    user_id_post = post.user_id
    post.deletar(db)
    
    # Criar notificação para o autor
    Notification.criar(
        db,
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
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Listar todos os posts (admin)"""
    posts = ForumPost.listar(db, pagina=pagina, tamanho_pagina=tamanho_pagina)
    return posts

# ========== ROTAS PARA PRÉ-CADASTRO ==========

@router.get("/pre-registrations/pending", response_model=List[PsychologistPreRegistrationResponse])
def listar_pre_cadastros_pendentes(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Listar pré-cadastros pendentes"""
    pre_registrations = PsychologistPreRegistration.listar_pendentes(db)
    return pre_registrations

@router.post("/pre-registrations/{id_pre_cadastro}/approve", response_model=PsychologistResponse)
def aprovar_pre_cadastro(
    id_pre_cadastro: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Aprovar pré-cadastro e criar perfil de psicólogo"""
    pre_reg = PsychologistPreRegistration.obter_por_id(db, id_pre_cadastro)
    
    if not pre_reg or pre_reg.status != 'pending':
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found or already processed"
        )
    
    # Parse specialty_ids e approach_ids
    specialty_ids = json.loads(pre_reg.specialty_ids) if pre_reg.specialty_ids else []
    approach_ids = json.loads(pre_reg.approach_ids) if pre_reg.approach_ids else []
    
    # Criar perfil de psicólogo
    psychologist = Psychologist.criar(
        db,
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
        is_verified=False
    )
    
    # Adicionar especialidades e abordagens
    if specialty_ids:
        specialties = Specialty.obter_por_ids(db, specialty_ids)
        psychologist.specialties = specialties
    
    if approach_ids:
        approaches = Approach.obter_por_ids(db, approach_ids)
        psychologist.approaches = approaches
    
    # Atualizar status do pré-cadastro
    pre_reg.atualizar(db, status='approved')
    
    # Criar notificação para o usuário
    Notification.criar(
        db,
        user_id=psychologist.user_id,
        title="Pré-cadastro Aprovado",
        message="Seu pré-cadastro foi aprovado e seu perfil de psicólogo foi criado.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist",
        is_read=False
    )
    
    # Recarregar com relacionamentos
    psychologist = Psychologist.obter_por_id(db, psychologist.id, carregar_relacionamentos=True)
    
    return psychologist

@router.post("/pre-registrations/{id_pre_cadastro}/reject")
def rejeitar_pre_cadastro(
    id_pre_cadastro: int,
    motivo_rejeicao: str,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_admin)
):
    """Rejeitar pré-cadastro"""
    pre_registration = PsychologistPreRegistration.obter_por_id(db, id_pre_cadastro)
    
    if not pre_registration:
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found"
        )
    
    pre_registration.atualizar(db, status='rejected', rejection_reason=motivo_rejeicao)
    
    # Criar notificação para o usuário
    Notification.criar(
        db,
        user_id=pre_registration.user_id,
        title="Pré-cadastro Rejeitado",
        message=f"Seu pré-cadastro foi rejeitado. Motivo: {motivo_rejeicao}",
        type="system",
        related_id=id_pre_cadastro,
        related_type="pre_registration",
        is_read=False
    )
    
    return {"message": "Pre-registration rejected", "pre_registration": pre_registration}


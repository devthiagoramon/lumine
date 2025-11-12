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
from app.services.psychologist_service import PsychologistService
from app.services.pre_registration_service import PreRegistrationService
from app.services.forum_service import ForumService
from app.services.notification_service import NotificationService

router = APIRouter()

# ========== ROTAS PARA VALIDAÇÃO DE PSICÓLOGOS ==========

@router.get("/psychologists/pending", response_model=List[PsychologistResponse])
def list_pending_psychologists(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Lista todos os psicólogos pendentes de validação"""
    psychologists = db.query(Psychologist).options(
        joinedload(Psychologist.user),
        joinedload(Psychologist.specialties),
        joinedload(Psychologist.approaches)
    ).filter(
        Psychologist.is_verified == False
    ).all()
    return psychologists

@router.put("/psychologists/{psychologist_id}/verify", response_model=PsychologistResponse)
def verify_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Valida o cadastro de um psicólogo"""
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist_id,
        load_relationships=True
    )
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.is_verified = True
    db.commit()
    db.refresh(psychologist)
    
    # Criar notificação para o psicólogo
    NotificationService.create_notification(
        db=db,
        user_id=psychologist.user_id,
        title="Cadastro Verificado",
        message="Seu cadastro foi verificado e aprovado pela administração.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist"
    )
    
    # Recarregar com relacionamentos
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist_id,
        load_relationships=True
    )
    
    return psychologist

@router.put("/psychologists/{psychologist_id}/unverify", response_model=PsychologistResponse)
def unverify_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Remove a validação de um psicólogo"""
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist_id,
        load_relationships=True
    )
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.is_verified = False
    db.commit()
    db.refresh(psychologist)
    
    # Criar notificação para o psicólogo
    NotificationService.create_notification(
        db=db,
        user_id=psychologist.user_id,
        title="Cadastro Desverificado",
        message="Seu cadastro foi desverificado pela administração.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist"
    )
    
    # Recarregar com relacionamentos
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist_id,
        load_relationships=True
    )
    
    return psychologist

# ========== ROTAS PARA GERENCIAMENTO DE FÓRUNS ==========

@router.delete("/forum/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_as_admin(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Deletar post como administrador"""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    success = ForumService.delete_post(
        db=db,
        post_id=post_id,
        user_id=post.user_id  # Usar user_id do post para permitir exclusão
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Criar notificação para o autor
    NotificationService.create_notification(
        db=db,
        user_id=post.user_id,
        title="Post Removido",
        message="Seu post foi removido pela administração.",
        type="system",
        related_id=post_id,
        related_type="forum_post"
    )
    
    return None

@router.get("/forum/posts", response_model=List[ForumPostResponse])
def list_all_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Listar todos os posts (admin)"""
    posts = ForumService.list_posts(
        db=db,
        category=None,
        search=None,
        page=page,
        page_size=page_size
    )
    
    # Adicionar contagem de comentários
    for post in posts:
        comments_count = ForumService.get_comments_count(db=db, post_id=post.id)
        post.comments_count = comments_count
    
    return posts

# ========== ROTAS PARA PRÉ-CADASTRO ==========

@router.get("/pre-registrations/pending", response_model=List[PsychologistPreRegistrationResponse])
def list_pending_pre_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Listar pré-cadastros pendentes"""
    pre_registrations = db.query(PsychologistPreRegistration).filter(
        PsychologistPreRegistration.status == 'pending'
    ).order_by(PsychologistPreRegistration.created_at.desc()).all()
    
    return pre_registrations

@router.post("/pre-registrations/{pre_registration_id}/approve", response_model=PsychologistResponse)
def approve_pre_registration(
    pre_registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Aprovar pré-cadastro e criar perfil de psicólogo"""
    psychologist = PreRegistrationService.approve_pre_registration(
        db=db,
        pre_registration_id=pre_registration_id
    )
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found or already processed"
        )
    
    # Criar notificação para o usuário
    NotificationService.create_notification(
        db=db,
        user_id=psychologist.user_id,
        title="Pré-cadastro Aprovado",
        message="Seu pré-cadastro foi aprovado e seu perfil de psicólogo foi criado.",
        type="system",
        related_id=psychologist.id,
        related_type="psychologist"
    )
    
    # Recarregar com relacionamentos
    psychologist = PsychologistService.get_psychologist_by_id(
        db=db,
        psychologist_id=psychologist.id,
        load_relationships=True
    )
    
    return psychologist

@router.post("/pre-registrations/{pre_registration_id}/reject")
def reject_pre_registration(
    pre_registration_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin)
):
    """Rejeitar pré-cadastro"""
    pre_registration = PreRegistrationService.reject_pre_registration(
        db=db,
        pre_registration_id=pre_registration_id,
        rejection_reason=rejection_reason
    )
    
    if not pre_registration:
        raise HTTPException(
            status_code=404,
            detail="Pre-registration not found"
        )
    
    # Criar notificação para o usuário
    NotificationService.create_notification(
        db=db,
        user_id=pre_registration.user_id,
        title="Pré-cadastro Rejeitado",
        message=f"Seu pré-cadastro foi rejeitado. Motivo: {rejection_reason}",
        type="system",
        related_id=pre_registration_id,
        related_type="pre_registration"
    )
    
    return {"message": "Pre-registration rejected", "pre_registration": pre_registration}


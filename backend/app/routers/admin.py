from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app import auth, schemas, models
from sqlalchemy import func, desc

router = APIRouter()

# ========== ROTAS PARA VALIDAÇÃO DE PSICÓLOGOS ==========

@router.get("/psychologists/pending", response_model=List[schemas.PsychologistResponse])
def list_pending_psychologists(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Lista todos os psicólogos pendentes de validação"""
    psychologists = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(
        models.Psychologist.is_verified == False
    ).all()
    return psychologists

@router.put("/psychologists/{psychologist_id}/verify", response_model=schemas.PsychologistResponse)
def verify_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Valida o cadastro de um psicólogo"""
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.is_verified = True
    db.commit()
    db.refresh(psychologist)
    
    # Recarregar com relacionamentos
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(models.Psychologist.id == psychologist_id).first()
    
    return psychologist

@router.put("/psychologists/{psychologist_id}/unverify", response_model=schemas.PsychologistResponse)
def unverify_psychologist(
    psychologist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Remove a validação de um psicólogo"""
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    psychologist.is_verified = False
    db.commit()
    db.refresh(psychologist)
    
    # Recarregar com relacionamentos
    psychologist = db.query(models.Psychologist).options(
        joinedload(models.Psychologist.user),
        joinedload(models.Psychologist.specialties),
        joinedload(models.Psychologist.approaches)
    ).filter(models.Psychologist.id == psychologist_id).first()
    
    return psychologist

# ========== ROTAS PARA GERENCIAMENTO DE FÓRUNS ==========

@router.post("/forum/posts", response_model=schemas.ForumPostResponse, status_code=status.HTTP_201_CREATED)
def create_post_as_admin(
    post: schemas.ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Cria um post no fórum como administrador"""
    db_post = models.ForumPost(
        user_id=current_user.id,
        **post.dict()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Recarregar com relacionamentos
    db_post = db.query(models.ForumPost).options(
        joinedload(models.ForumPost.user)
    ).filter(models.ForumPost.id == db_post.id).first()
    
    # Contar comentários
    comments_count = db.query(func.count(models.ForumComment.id)).filter(
        models.ForumComment.post_id == db_post.id
    ).scalar()
    db_post.comments_count = comments_count
    
    return db_post

@router.put("/forum/posts/{post_id}", response_model=schemas.ForumPostResponse)
def update_post_as_admin(
    post_id: int,
    post_update: schemas.ForumPostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Edita um post no fórum como administrador (pode editar qualquer post)"""
    post = db.query(models.ForumPost).filter(
        models.ForumPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    update_data = post_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    # Recarregar com relacionamentos
    post = db.query(models.ForumPost).options(
        joinedload(models.ForumPost.user)
    ).filter(models.ForumPost.id == post_id).first()
    
    comments_count = db.query(func.count(models.ForumComment.id)).filter(
        models.ForumComment.post_id == post.id
    ).scalar()
    post.comments_count = comments_count
    
    return post

@router.delete("/forum/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_as_admin(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    """Remove um post no fórum como administrador (pode remover qualquer post)"""
    post = db.query(models.ForumPost).filter(
        models.ForumPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return None


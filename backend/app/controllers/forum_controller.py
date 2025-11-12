"""
Forum Controller - Endpoints de fórum
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import auth
from app.schemas import (
    ForumPostCreate, ForumPostUpdate, ForumPostResponse,
    ForumCommentCreate, ForumCommentResponse
)
from app.models.user import User
from app.models.forum_post import ForumPost
from app.models.forum_comment import ForumComment
from app.services.forum_service import ForumService

router = APIRouter()

@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar post no fórum"""
    post_data = post.dict()
    db_post = ForumService.create_post(
        db=db,
        user_id=current_user.id,
        post_data=post_data
    )
    
    # Recarregar com relacionamentos
    from sqlalchemy.orm import joinedload
    db_post = db.query(ForumPost).options(
        joinedload(ForumPost.user)
    ).filter(ForumPost.id == db_post.id).first()
    
    # Contar comentários
    comments_count = ForumService.get_comments_count(db=db, post_id=db_post.id)
    db_post.comments_count = comments_count
    
    return db_post

@router.get("/posts", response_model=List[ForumPostResponse])
def list_posts(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Listar posts do fórum"""
    posts = ForumService.list_posts(
        db=db,
        category=category,
        search=search,
        page=page,
        page_size=page_size
    )
    
    # Adicionar contagem de comentários
    for post in posts:
        comments_count = ForumService.get_comments_count(db=db, post_id=post.id)
        post.comments_count = comments_count
    
    return posts

@router.get("/posts/{post_id}", response_model=ForumPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Obter post por ID"""
    post = ForumService.get_post_by_id(
        db=db,
        post_id=post_id,
        increment_views=True
    )
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Contar comentários
    comments_count = ForumService.get_comments_count(db=db, post_id=post.id)
    post.comments_count = comments_count
    
    return post

@router.put("/posts/{post_id}", response_model=ForumPostResponse)
def update_post(
    post_id: int,
    post_update: ForumPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Atualizar post"""
    post = db.query(ForumPost).filter(
        ForumPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own posts"
        )
    
    update_data = post_update.dict(exclude_unset=True)
    db_post = ForumService.update_post(
        db=db,
        post=post,
        update_data=update_data
    )
    
    # Recarregar com relacionamentos
    from sqlalchemy.orm import joinedload
    db_post = db.query(ForumPost).options(
        joinedload(ForumPost.user)
    ).filter(ForumPost.id == post_id).first()
    
    comments_count = ForumService.get_comments_count(db=db, post_id=db_post.id)
    db_post.comments_count = comments_count
    
    return db_post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Deletar post"""
    success = ForumService.delete_post(
        db=db,
        post_id=post_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    return None

@router.post("/posts/{post_id}/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: ForumCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar comentário"""
    # Verificar se post existe
    post = ForumService.get_post_by_id(db=db, post_id=post_id, increment_views=False)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    comment_data = comment.dict()
    db_comment = ForumService.create_comment(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
        comment_data=comment_data
    )
    
    # Recarregar com relacionamentos
    from sqlalchemy.orm import joinedload
    db_comment = db.query(ForumComment).options(
        joinedload(ForumComment.user)
    ).filter(ForumComment.id == db_comment.id).first()
    
    return db_comment

@router.get("/posts/{post_id}/comments", response_model=List[ForumCommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Obter comentários de um post"""
    comments = ForumService.get_comments_by_post(
        db=db,
        post_id=post_id
    )
    return comments

@router.get("/categories")
def get_categories():
    """Obter categorias do fórum"""
    return {
        "categories": [
            {"value": "geral", "label": "Geral"},
            {"value": "ansiedade", "label": "Ansiedade"},
            {"value": "depressao", "label": "Depressão"},
            {"value": "relacionamentos", "label": "Relacionamentos"},
            {"value": "autoestima", "label": "Autoestima"},
            {"value": "estresse", "label": "Estresse"},
            {"value": "luto", "label": "Luto"},
            {"value": "trauma", "label": "Trauma"},
            {"value": "outros", "label": "Outros"}
        ]
    }


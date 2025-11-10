from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app import auth, schemas, models
from sqlalchemy import func, desc

router = APIRouter()

@router.post("/posts", response_model=schemas.ForumPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
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

@router.get("/posts", response_model=List[schemas.ForumPostResponse])
def list_posts(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.ForumPost).options(
        joinedload(models.ForumPost.user)
    )
    
    if category:
        query = query.filter(models.ForumPost.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.ForumPost.title.ilike(search_term)) |
            (models.ForumPost.content.ilike(search_term))
        )
    
    # Contar comentários para cada post
    posts = query.order_by(desc(models.ForumPost.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    for post in posts:
        comments_count = db.query(func.count(models.ForumComment.id)).filter(
            models.ForumComment.post_id == post.id
        ).scalar()
        post.comments_count = comments_count
    
    return posts

@router.get("/posts/{post_id}", response_model=schemas.ForumPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(models.ForumPost).options(
        joinedload(models.ForumPost.user)
    ).filter(models.ForumPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Incrementar views
    post.views += 1
    db.commit()
    db.refresh(post)
    
    # Contar comentários
    comments_count = db.query(func.count(models.ForumComment.id)).filter(
        models.ForumComment.post_id == post.id
    ).scalar()
    post.comments_count = comments_count
    
    return post

@router.put("/posts/{post_id}", response_model=schemas.ForumPostResponse)
def update_post(
    post_id: int,
    post_update: schemas.ForumPostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    post = db.query(models.ForumPost).filter(
        models.ForumPost.id == post_id
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

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    post = db.query(models.ForumPost).filter(
        models.ForumPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own posts"
        )
    
    db.delete(post)
    db.commit()
    
    return None

@router.post("/posts/{post_id}/comments", response_model=schemas.ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: schemas.ForumCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se post existe
    post = db.query(models.ForumPost).filter(
        models.ForumPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    db_comment = models.ForumComment(
        post_id=post_id,
        user_id=current_user.id,
        **comment.dict()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Recarregar com relacionamentos
    db_comment = db.query(models.ForumComment).options(
        joinedload(models.ForumComment.user)
    ).filter(models.ForumComment.id == db_comment.id).first()
    
    return db_comment

@router.get("/posts/{post_id}/comments", response_model=List[schemas.ForumCommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    comments = db.query(models.ForumComment).options(
        joinedload(models.ForumComment.user)
    ).filter(
        models.ForumComment.post_id == post_id
    ).order_by(models.ForumComment.created_at.asc()).all()
    
    return comments

@router.get("/categories")
def get_categories():
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


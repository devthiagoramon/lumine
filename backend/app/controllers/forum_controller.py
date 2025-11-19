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
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
def criar_post(
    post: ForumPostCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar post no fórum"""
    db_post = ForumPost.criar(
        db,
        user_id=usuario_atual.id,
        title=post.title,
        content=post.content,
        category=post.category,
        is_anonymous=post.is_anonymous
    )
    
    # Recarregar com relacionamentos e contagem de comentários
    db_post = ForumPost.obter_por_id(db, db_post.id)
    
    return db_post

@router.get("/posts", response_model=List[ForumPostResponse])
def listar_posts(
    categoria: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Listar posts do fórum"""
    posts = ForumPost.listar(db, categoria=categoria, busca=busca, pagina=pagina, tamanho_pagina=tamanho_pagina)
    return posts

@router.get("/posts/{id_post}", response_model=ForumPostResponse)
def obter_post(
    id_post: int,
    db: Session = Depends(get_db)
):
    """Obter post por ID"""
    post = ForumPost.obter_por_id(db, id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    post.incrementar_visualizacao(db)
    
    return post

@router.put("/posts/{id_post}", response_model=ForumPostResponse)
def atualizar_post(
    id_post: int,
    atualizacao_post: ForumPostUpdate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar post"""
    post = ForumPost.obter_por_id(db, id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if post.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own posts"
        )
    
    update_data = atualizacao_post.dict(exclude_unset=True)
    post.atualizar(db, **update_data)
    
    # Recarregar com relacionamentos
    db_post = ForumPost.obter_por_id(db, id_post)
    
    return db_post

@router.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_post(
    id_post: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar post"""
    post = ForumPost.obter_por_id(db, id_post)
    
    if not post or post.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    post.deletar(db)
    return None

@router.post("/posts/{id_post}/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def criar_comentario(
    id_post: int,
    comentario: ForumCommentCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar comentário"""
    # Verificar se post existe
    post = ForumPost.obter_por_id(db, id_post)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    db_comment = ForumComment.criar(
        db,
        post_id=id_post,
        user_id=usuario_atual.id,
        content=comentario.content,
        is_anonymous=comentario.is_anonymous
    )
    
    # Recarregar com relacionamentos
    db_comment = ForumComment.obter_por_id(db, db_comment.id, carregar_relacionamentos=True)
    
    return db_comment

@router.get("/posts/{id_post}/comments", response_model=List[ForumCommentResponse])
def obter_comentarios(
    id_post: int,
    db: Session = Depends(get_db)
):
    """Obter comentários de um post"""
    comments = ForumComment.listar_por_post(db, id_post)
    return comments

@router.get("/categories")
def obter_categorias():
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


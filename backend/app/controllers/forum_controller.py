"""
Forum Controller - Endpoints de fórum
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
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
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar post no fórum"""
    post_db = ForumPost.criar(
        user_id=usuario_atual.id,
        title=post.title,
        content=post.content,
        category=post.category,
        is_anonymous=post.is_anonymous
    )
    
    # Recarregar com relacionamentos e contagem de comentários
    post_db = ForumPost.obter_por_id(post_db.id)
    
    return post_db

@router.get("/posts", response_model=List[ForumPostResponse])
def listar_posts(
    categoria: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100)
):
    """Listar posts do fórum"""
    posts = ForumPost.listar(categoria=categoria, busca=busca, pagina=pagina, tamanho_pagina=tamanho_pagina)
    return posts

@router.get("/posts/{id_post}", response_model=ForumPostResponse)
def obter_post(
    id_post: int
):
    """Obter post por ID"""
    post = ForumPost.obter_por_id(id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post não encontrado"
        )
    
    post.incrementar_visualizacao()
    
    return post

@router.put("/posts/{id_post}", response_model=ForumPostResponse)
def atualizar_post(
    id_post: int,
    atualizacao_post: ForumPostUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar post"""
    post = ForumPost.obter_por_id(id_post)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post não encontrado"
        )
    
    if post.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode editar seus próprios posts"
        )
    
    dados_atualizacao = atualizacao_post.dict(exclude_unset=True)
    post.atualizar(**dados_atualizacao)
    
    # Recarregar com relacionamentos
    post_db = ForumPost.obter_por_id(id_post)
    
    return post_db

@router.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_post(
    id_post: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar post"""
    post = ForumPost.obter_por_id(id_post)
    
    if not post or post.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=404,
            detail="Post não encontrado"
        )
    
    post.deletar()
    return None

@router.post("/posts/{id_post}/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def criar_comentario(
    id_post: int,
    comentario: ForumCommentCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar comentário"""
    # Verificar se post existe
    post = ForumPost.obter_por_id(id_post)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post não encontrado"
        )
    
    comentario_db = ForumComment.criar(
        post_id=id_post,
        user_id=usuario_atual.id,
        content=comentario.content,
        is_anonymous=comentario.is_anonymous
    )
    
    # Recarregar com relacionamentos
    comentario_db = ForumComment.obter_por_id_com_relacionamentos(comentario_db.id)
    
    return comentario_db

@router.get("/posts/{id_post}/comments", response_model=List[ForumCommentResponse])
def obter_comentarios(
    id_post: int
):
    """Obter comentários de um post"""
    comentarios = ForumComment.listar_por_post(id_post)
    return comentarios

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


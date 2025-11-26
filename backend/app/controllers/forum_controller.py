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
from app.models.usuario import User
from app.models.post_forum import ForumPost
from app.models.comentario_forum import ForumComment
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
def criar_post(
    post: ForumPostCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar post no fórum"""
    import sys
    import traceback
    
    try:
        print(f"DEBUG: Criando post - Título: {post.title}, Categoria: {post.category}, Anônimo: {post.is_anonymous}", file=sys.stderr, flush=True)
        
        post_objeto = ForumPost.criar(
            id_usuario=usuario_atual.id,
            titulo=post.title,
            conteudo=post.content,
            categoria=post.category,
            eh_anonimo=post.is_anonymous
        )
        
        print(f"DEBUG: Post criado com sucesso - ID: {post_objeto.id}", file=sys.stderr, flush=True)
        
        # Recarregar com relacionamentos e contagem de comentários
        post_objeto = ForumPost.obter_por_id(post_objeto.id)
        
        # Serializar manualmente para garantir que funciona
        from app.schemas.forum import ForumPostResponse
        post_dict = ForumPostResponse.model_validate(post_objeto).model_dump(by_alias=True, mode='json')
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content=post_dict, status_code=status.HTTP_201_CREATED)
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Erro ao criar post: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar post: {str(e)}"
        )

@router.get("/posts", response_model=List[ForumPostResponse])
def listar_posts(
    categoria: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100)
):
    """Listar posts do fórum"""
    posts = ForumPost.listar(categoria=categoria, busca=busca, pagina=pagina, tamanho_pagina=tamanho_pagina)
    
    # Serializar manualmente para garantir que os aliases sejam usados
    try:
        from app.schemas.forum import ForumPostResponse
        serialized = []
        for post in posts:
            post_dict = ForumPostResponse.model_validate(post).model_dump(by_alias=True, mode='json')
            serialized.append(post_dict)
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content=serialized)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar posts: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        # Fallback: retornar sem serialização manual
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
    
    if post.id_usuario != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode editar seus próprios posts"
        )
    
    # Mapear campos do schema para o modelo
    dados_atualizacao = {}
    if atualizacao_post.title is not None:
        dados_atualizacao['titulo'] = atualizacao_post.title
    if atualizacao_post.content is not None:
        dados_atualizacao['conteudo'] = atualizacao_post.content
    if atualizacao_post.category is not None:
        dados_atualizacao['categoria'] = atualizacao_post.category
    
    post.atualizar(**dados_atualizacao)
    
    # Recarregar com relacionamentos
    post_objeto = ForumPost.obter_por_id(id_post)
    
    return post_objeto

@router.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_post(
    id_post: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar post"""
    post = ForumPost.obter_por_id(id_post)
    
    if not post or post.id_usuario != usuario_atual.id:
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
    
    comentario_created = ForumComment.criar(
        id_post=id_post,
        id_usuario=usuario_atual.id,
        conteudo=comentario.content,
        eh_anonimo=comentario.is_anonymous
    )
    
    # Recarregar com relacionamentos
    comentario_created = ForumComment.obter_por_id_com_relacionamentos(comentario_created.id)
    
    return comentario_created

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


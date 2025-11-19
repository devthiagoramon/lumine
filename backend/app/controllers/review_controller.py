"""
Review Controller - Endpoints de avaliações
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import ReviewCreate, ReviewResponse
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.review import Review
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    avaliacao: ReviewCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar avaliação"""
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(db, avaliacao.psychologist_id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Verificar se já avaliou
    avaliacao_existente = Review.verificar_existente(db, avaliacao.psychologist_id, usuario_atual.id)
    if avaliacao_existente:
        raise HTTPException(
            status_code=400,
            detail="Você já avaliou este psicólogo"
        )
    
    # Validar rating
    if avaliacao.rating < 1 or avaliacao.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Avaliação deve estar entre 1 e 5"
        )
    
    # Criar avaliação
    avaliacao_db = Review.criar(
        db,
        psychologist_id=avaliacao.psychologist_id,
        user_id=usuario_atual.id,
        rating=avaliacao.rating,
        comment=avaliacao.comment
    )
    
    # Atualizar rating do psicólogo
    media_rating = Review.calcular_rating_medio(db, avaliacao.psychologist_id)
    total_avaliacoes = Review.contar_total(db, avaliacao.psychologist_id)
    
    psicologo.atualizar(db, rating=media_rating, total_reviews=total_avaliacoes)
    
    # Recarregar com relacionamentos
    avaliacao_db = Review.obter_por_id(db, avaliacao_db.id, carregar_relacionamentos=True)
    
    return avaliacao_db

@router.get("/psicologo/{id_psicologo}", response_model=List[ReviewResponse])
def obter_avaliacoes_psicologo(
    id_psicologo: int,
    pular: int = 0,
    limite: int = 20,
    db: Session = Depends(get_db)
):
    """Obter avaliações de um psicólogo"""
    avaliacoes = Review.listar_por_psicologo(db, id_psicologo)
    # Aplicar paginação manualmente (os métodos dos models retornam todas)
    avaliacoes = avaliacoes[pular:pular+limite]
    return avaliacoes

@router.get("/minhas-avaliacoes", response_model=List[ReviewResponse])
def obter_minhas_avaliacoes(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter minhas avaliações"""
    avaliacoes = Review.listar_por_usuario(db, usuario_atual.id)
    return avaliacoes

@router.delete("/{id_avaliacao}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_avaliacao(
    id_avaliacao: int,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar avaliação"""
    avaliacao = Review.obter_por_id(db, id_avaliacao)
    
    if not avaliacao or avaliacao.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada"
        )
    
    id_psicologo = avaliacao.psychologist_id
    avaliacao.deletar(db)
    
    # Atualizar rating do psicólogo
    psicologo = Psychologist.obter_por_id(db, id_psicologo)
    
    if psicologo:
        media_rating = Review.calcular_rating_medio(db, id_psicologo)
        total_avaliacoes = Review.contar_total(db, id_psicologo)
        
        psicologo.atualizar(db, rating=media_rating, total_reviews=total_avaliacoes)
    
    return None


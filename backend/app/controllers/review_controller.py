"""
Review Controller - Endpoints de avaliações
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
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
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar avaliação"""
    # Verificar se psicólogo existe
    psicologo = Psychologist.obter_por_id(avaliacao.psychologist_id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    
    # Verificar se já avaliou
    avaliacao_existente = Review.verificar_existente(avaliacao.psychologist_id, usuario_atual.id)
    if avaliacao_existente:
        raise HTTPException(
            status_code=400,
            detail="Você já avaliou este psicólogo"
        )
    
    # Verificar se o usuário teve pelo menos uma consulta concluída com este psicólogo
    from app.models.appointment import Appointment
    consultas_completadas = Appointment.listar_por_usuario(usuario_atual.id, status='completed')
    consulta_com_psicologo = any(
        apt.psychologist_id == avaliacao.psychologist_id 
        for apt in consultas_completadas
    )
    
    if not consulta_com_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Você só pode avaliar psicólogos com os quais já teve consultas concluídas"
        )
    
    # Validar rating
    if avaliacao.rating < 1 or avaliacao.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Avaliação deve estar entre 1 e 5"
        )
    
    # Criar avaliação
    avaliacao_created = Review.criar(
        psychologist_id=avaliacao.psychologist_id,
        user_id=usuario_atual.id,
        rating=avaliacao.rating,
        comment=avaliacao.comment
    )
    
    # Atualizar rating do psicólogo
    media_rating = Review.calcular_rating_medio(avaliacao.psychologist_id)
    total_avaliacoes = Review.contar_total(avaliacao.psychologist_id)
    
    psicologo.atualizar(rating=media_rating, total_reviews=total_avaliacoes)
    
    # Recarregar com relacionamentos
    avaliacao_object = Review.obter_por_id_com_relacionamentos(avaliacao_created.id)
    
    return avaliacao_object

@router.get("/psicologo/{id_psicologo}", response_model=List[ReviewResponse])
def obter_avaliacoes_psicologo(
    id_psicologo: int,
    pular: int = 0,
    limite: int = 20
):
    """Obter avaliações de um psicólogo"""
    avaliacoes = Review.listar_por_psicologo(id_psicologo)
    # Aplicar paginação manualmente (os métodos dos models retornam todas)
    avaliacoes = avaliacoes[pular:pular+limite]
    return avaliacoes

@router.get("/minhas-avaliacoes", response_model=List[ReviewResponse])
def obter_minhas_avaliacoes(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter minhas avaliações"""
    avaliacoes = Review.listar_por_usuario(usuario_atual.id)
    return avaliacoes

@router.delete("/{id_avaliacao}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_avaliacao(
    id_avaliacao: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar avaliação"""
    avaliacao = Review.obter_por_id_com_relacionamentos(id_avaliacao)
    
    if not avaliacao or avaliacao.user_id != usuario_atual.id:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada"
        )
    
    id_psicologo = avaliacao.psychologist_id
    avaliacao.deletar()
    
    # Atualizar rating do psicólogo
    psicologo = Psychologist.obter_por_id(id_psicologo)
    
    if psicologo:
        media_rating = Review.calcular_rating_medio(id_psicologo)
        total_avaliacoes = Review.contar_total(id_psicologo)
        
        psicologo.atualizar(rating=media_rating, total_reviews=total_avaliacoes)
    
    return None


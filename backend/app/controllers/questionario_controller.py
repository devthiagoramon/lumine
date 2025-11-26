"""
Questionnaire Controller - Endpoints de questionário
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import auth
from app.schemas import QuestionnaireCreate, QuestionnaireResponse
from app.models.usuario import User
from app.models.questionario import Questionnaire

router = APIRouter()

@router.post("/", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
def criar_questionario(
    questionario: QuestionnaireCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Responder questionário de autopercepção"""
    # Validar respostas (1-5)
    respostas = [
        questionario.question_1, questionario.question_2, questionario.question_3,
        questionario.question_4, questionario.question_5, questionario.question_6,
        questionario.question_7, questionario.question_8, questionario.question_9,
        questionario.question_10
    ]
    
    for resposta in respostas:
        if resposta < 1 or resposta > 5:
            raise HTTPException(
                status_code=400,
                detail="Todas as respostas devem estar entre 1 e 5"
            )
    
    # Calcular score total
    pontuacao_total = sum(respostas)
    
    # Calcular recomendação
    if pontuacao_total <= 20:
        recomendacao = "Você está se sentindo muito bem! Continue cuidando da sua saúde mental."
    elif pontuacao_total <= 30:
        recomendacao = "Você está se sentindo bem, mas pode se beneficiar de algumas práticas de autocuidado."
    elif pontuacao_total <= 40:
        recomendacao = "Considere buscar apoio profissional. A terapia pode ajudá-lo a lidar melhor com seus sentimentos."
    else:
        recomendacao = "É importante buscar ajuda profissional. Um psicólogo pode oferecer o suporte necessário."
    
    # Criar questionário
    questionario_created = Questionnaire.criar(
        user_id=usuario_atual.id,
        question_1=questionario.question_1,
        question_2=questionario.question_2,
        question_3=questionario.question_3,
        question_4=questionario.question_4,
        question_5=questionario.question_5,
        question_6=questionario.question_6,
        question_7=questionario.question_7,
        question_8=questionario.question_8,
        question_9=questionario.question_9,
        question_10=questionario.question_10,
        total_score=pontuacao_total,
        recommendation=recomendacao
    )
    return questionario_created

@router.get("/", response_model=List[QuestionnaireResponse])
def obter_meus_questionarios(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meus questionários"""
    questionarios = Questionnaire.listar_por_usuario(usuario_atual.id)
    return questionarios

@router.get("/mais-recente", response_model=QuestionnaireResponse)
def obter_questionario_mais_recente(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter questionário mais recente"""
    questionario = Questionnaire.obter_mais_recente(usuario_atual.id)
    
    if not questionario:
        raise HTTPException(
            status_code=404,
            detail="Nenhum questionário encontrado"
        )
    
    return questionario


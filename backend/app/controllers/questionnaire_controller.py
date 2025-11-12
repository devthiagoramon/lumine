"""
Questionnaire Controller - Endpoints de questionário
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import auth
from app.schemas import QuestionnaireCreate, QuestionnaireResponse
from app.models.user import User
from app.services.questionnaire_service import QuestionnaireService

router = APIRouter()

@router.post("/", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
def create_questionnaire(
    questionnaire: QuestionnaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Responder questionário de autopercepção"""
    # Validar respostas (1-5)
    answers = [
        questionnaire.question_1, questionnaire.question_2, questionnaire.question_3,
        questionnaire.question_4, questionnaire.question_5, questionnaire.question_6,
        questionnaire.question_7, questionnaire.question_8, questionnaire.question_9,
        questionnaire.question_10
    ]
    
    for answer in answers:
        if answer < 1 or answer > 5:
            raise HTTPException(
                status_code=400,
                detail="All answers must be between 1 and 5"
            )
    
    # Criar questionário usando service
    answers_dict = {
        f'question_{i+1}': answers[i]
        for i in range(10)
    }
    db_questionnaire = QuestionnaireService.create_questionnaire(
        db=db,
        user_id=current_user.id,
        answers=answers_dict
    )
    
    return db_questionnaire

@router.get("/", response_model=List[QuestionnaireResponse])
def get_my_questionnaires(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter meus questionários"""
    questionnaires = QuestionnaireService.get_questionnaires_by_user(
        db=db,
        user_id=current_user.id
    )
    return questionnaires

@router.get("/latest", response_model=QuestionnaireResponse)
def get_latest_questionnaire(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter questionário mais recente"""
    questionnaire = QuestionnaireService.get_latest_questionnaire(
        db=db,
        user_id=current_user.id
    )
    
    if not questionnaire:
        raise HTTPException(
            status_code=404,
            detail="No questionnaire found"
        )
    
    return questionnaire


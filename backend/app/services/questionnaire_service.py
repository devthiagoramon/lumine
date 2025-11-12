"""
Service para gerenciar questionários
"""
from sqlalchemy.orm import Session
from app.models.questionnaire import Questionnaire
from typing import List, Optional

class QuestionnaireService:
    @staticmethod
    def calculate_recommendation(total_score: int) -> str:
        """Calcula recomendação baseada no score total"""
        if total_score <= 20:
            return "Você está se sentindo muito bem! Continue cuidando da sua saúde mental."
        elif total_score <= 30:
            return "Você está se sentindo bem, mas pode se beneficiar de algumas práticas de autocuidado."
        elif total_score <= 40:
            return "Considere buscar apoio profissional. A terapia pode ajudá-lo a lidar melhor com seus sentimentos."
        else:
            return "É importante buscar ajuda profissional. Um psicólogo pode oferecer o suporte necessário."
    
    @staticmethod
    def create_questionnaire(
        db: Session,
        user_id: int,
        answers: dict
    ) -> Questionnaire:
        """Criar questionário"""
        # Calcular score total
        total_score = sum([
            answers.get(f'question_{i}', 0)
            for i in range(1, 11)
        ])
        recommendation = QuestionnaireService.calculate_recommendation(total_score)
        
        questionnaire = Questionnaire(
            user_id=user_id,
            **answers,
            total_score=total_score,
            recommendation=recommendation
        )
        db.add(questionnaire)
        db.commit()
        db.refresh(questionnaire)
        return questionnaire
    
    @staticmethod
    def get_questionnaires_by_user(
        db: Session,
        user_id: int
    ) -> List[Questionnaire]:
        """Obter questionários do usuário"""
        return db.query(Questionnaire).filter(
            Questionnaire.user_id == user_id
        ).order_by(Questionnaire.created_at.desc()).all()
    
    @staticmethod
    def get_latest_questionnaire(
        db: Session,
        user_id: int
    ) -> Optional[Questionnaire]:
        """Obter questionário mais recente"""
        return db.query(Questionnaire).filter(
            Questionnaire.user_id == user_id
        ).order_by(Questionnaire.created_at.desc()).first()


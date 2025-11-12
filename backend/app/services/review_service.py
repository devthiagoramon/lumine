"""
Service para gerenciar avaliações
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.review import Review
from app.models.psychologist import Psychologist
from typing import List, Optional

class ReviewService:
    @staticmethod
    def create_review(
        db: Session,
        psychologist_id: int,
        user_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Review:
        """Criar avaliação"""
        review = Review(
            psychologist_id=psychologist_id,
            user_id=user_id,
            rating=rating,
            comment=comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Atualizar rating do psicólogo
        ReviewService.update_psychologist_rating(db, psychologist_id)
        
        return review
    
    @staticmethod
    def update_psychologist_rating(db: Session, psychologist_id: int):
        """Atualizar rating do psicólogo"""
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.psychologist_id == psychologist_id
        ).scalar()
        total_reviews = db.query(func.count(Review.id)).filter(
            Review.psychologist_id == psychologist_id
        ).scalar()
        
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == psychologist_id
        ).first()
        
        if psychologist:
            psychologist.rating = float(avg_rating) if avg_rating else 0.0
            psychologist.total_reviews = total_reviews
            db.commit()
    
    @staticmethod
    def get_reviews_by_psychologist(
        db: Session,
        psychologist_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Review]:
        """Obter avaliações de um psicólogo"""
        return db.query(Review).options(
            joinedload(Review.user)
        ).filter(
            Review.psychologist_id == psychologist_id
        ).order_by(
            Review.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_reviews_by_user(db: Session, user_id: int) -> List[Review]:
        """Obter avaliações de um usuário"""
        return db.query(Review).options(
            joinedload(Review.user)
        ).filter(
            Review.user_id == user_id
        ).order_by(Review.created_at.desc()).all()
    
    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int) -> bool:
        """Deletar avaliação"""
        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()
        
        if not review:
            return False
        
        psychologist_id = review.psychologist_id
        db.delete(review)
        db.commit()
        
        # Atualizar rating do psicólogo
        ReviewService.update_psychologist_rating(db, psychologist_id)
        
        return True


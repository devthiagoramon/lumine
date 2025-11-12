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
from app.services.review_service import ReviewService

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Criar avaliação"""
    # Verificar se psicólogo existe
    psychologist = db.query(Psychologist).filter(
        Psychologist.id == review.psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Verificar se já avaliou
    from app.models.review import Review
    existing_review = db.query(Review).filter(
        Review.psychologist_id == review.psychologist_id,
        Review.user_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this psychologist"
        )
    
    # Validar rating
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    
    # Criar review usando service
    db_review = ReviewService.create_review(
        db=db,
        psychologist_id=review.psychologist_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    
    # Recarregar com relacionamentos
    from sqlalchemy.orm import joinedload
    db_review = db.query(Review).options(
        joinedload(Review.user)
    ).filter(Review.id == db_review.id).first()
    
    return db_review

@router.get("/psychologist/{psychologist_id}", response_model=List[ReviewResponse])
def get_psychologist_reviews(
    psychologist_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Obter avaliações de um psicólogo"""
    reviews = ReviewService.get_reviews_by_psychologist(
        db=db,
        psychologist_id=psychologist_id,
        skip=skip,
        limit=limit
    )
    return reviews

@router.get("/my-reviews", response_model=List[ReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Obter minhas avaliações"""
    reviews = ReviewService.get_reviews_by_user(
        db=db,
        user_id=current_user.id
    )
    return reviews

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Deletar avaliação"""
    success = ReviewService.delete_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    return None


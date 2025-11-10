from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import auth, schemas, models
from sqlalchemy import func

router = APIRouter()

@router.post("/", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verificar se psicólogo existe
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == review.psychologist_id
    ).first()
    if not psychologist:
        raise HTTPException(
            status_code=404,
            detail="Psychologist not found"
        )
    
    # Verificar se já avaliou
    existing_review = db.query(models.Review).filter(
        models.Review.psychologist_id == review.psychologist_id,
        models.Review.user_id == current_user.id
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
    
    # Criar review
    db_review = models.Review(
        psychologist_id=review.psychologist_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Atualizar rating do psicólogo
    avg_rating = db.query(func.avg(models.Review.rating)).filter(
        models.Review.psychologist_id == review.psychologist_id
    ).scalar()
    total_reviews = db.query(func.count(models.Review.id)).filter(
        models.Review.psychologist_id == review.psychologist_id
    ).scalar()
    
    psychologist.rating = float(avg_rating) if avg_rating else 0.0
    psychologist.total_reviews = total_reviews
    db.commit()
    
    # Recarregar com relacionamentos
    db_review = db.query(models.Review).options(
        joinedload(models.Review.user)
    ).filter(models.Review.id == db_review.id).first()
    
    return db_review

@router.get("/psychologist/{psychologist_id}", response_model=List[schemas.ReviewResponse])
def get_psychologist_reviews(
    psychologist_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    reviews = db.query(models.Review).options(
        joinedload(models.Review.user)
    ).filter(
        models.Review.psychologist_id == psychologist_id
    ).order_by(
        models.Review.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return reviews

@router.get("/my-reviews", response_model=List[schemas.ReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    reviews = db.query(models.Review).options(
        joinedload(models.Review.user)
    ).filter(
        models.Review.user_id == current_user.id
    ).order_by(
        models.Review.created_at.desc()
    ).all()
    
    return reviews

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    review = db.query(models.Review).filter(
        models.Review.id == review_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own reviews"
        )
    
    psychologist_id = review.psychologist_id
    db.delete(review)
    db.commit()
    
    # Atualizar rating do psicólogo
    avg_rating = db.query(func.avg(models.Review.rating)).filter(
        models.Review.psychologist_id == psychologist_id
    ).scalar()
    total_reviews = db.query(func.count(models.Review.id)).filter(
        models.Review.psychologist_id == psychologist_id
    ).scalar()
    
    psychologist = db.query(models.Psychologist).filter(
        models.Psychologist.id == psychologist_id
    ).first()
    if psychologist:
        psychologist.rating = float(avg_rating) if avg_rating else 0.0
        psychologist.total_reviews = total_reviews
        db.commit()
    
    return None


"""
Service para gerenciar favoritos
"""
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.psychologist import Psychologist
from typing import List

class FavoriteService:
    @staticmethod
    def add_favorite(
        db: Session,
        user_id: int,
        psychologist_id: int
    ) -> bool:
        """Adicionar psicólogo aos favoritos"""
        user = db.query(User).options(
            joinedload(User.favorite_psychologists)
        ).filter(User.id == user_id).first()
        
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == psychologist_id
        ).first()
        
        if not user or not psychologist:
            return False
        
        if psychologist in user.favorite_psychologists:
            return False  # Já está nos favoritos
        
        user.favorite_psychologists.append(psychologist)
        db.commit()
        return True
    
    @staticmethod
    def remove_favorite(
        db: Session,
        user_id: int,
        psychologist_id: int
    ) -> bool:
        """Remover psicólogo dos favoritos"""
        user = db.query(User).options(
            joinedload(User.favorite_psychologists)
        ).filter(User.id == user_id).first()
        
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == psychologist_id
        ).first()
        
        if not user or not psychologist:
            return False
        
        if psychologist in user.favorite_psychologists:
            user.favorite_psychologists.remove(psychologist)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_favorites(
        db: Session,
        user_id: int
    ) -> List[Psychologist]:
        """Obter favoritos do usuário"""
        user = db.query(User).options(
            joinedload(User.favorite_psychologists).joinedload(Psychologist.user),
            joinedload(User.favorite_psychologists).joinedload(Psychologist.specialties),
            joinedload(User.favorite_psychologists).joinedload(Psychologist.approaches)
        ).filter(User.id == user_id).first()
        
        return user.favorite_psychologists if user else []
    
    @staticmethod
    def is_favorite(
        db: Session,
        user_id: int,
        psychologist_id: int
    ) -> bool:
        """Verificar se psicólogo está nos favoritos"""
        user = db.query(User).options(
            joinedload(User.favorite_psychologists)
        ).filter(User.id == user_id).first()
        
        psychologist = db.query(Psychologist).filter(
            Psychologist.id == psychologist_id
        ).first()
        
        if not user or not psychologist:
            return False
        
        return psychologist in user.favorite_psychologists


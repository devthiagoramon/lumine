"""
Service para gerenciar usuários
"""
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Obter usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obter usuário por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Criar novo usuário"""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


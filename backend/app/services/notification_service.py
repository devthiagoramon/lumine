"""
Service para gerenciar notificações
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification
from typing import List, Optional
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        type: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None
    ) -> Notification:
        """Cria uma nova notificação"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            related_id=related_id,
            related_type=related_type,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Obtém notificações do usuário"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        """Marca notificação como lida"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Marca todas as notificações do usuário como lidas"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Conta notificações não lidas"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()


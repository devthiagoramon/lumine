"""
Service para gerenciar diário de emoções
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.emotion_diary import EmotionDiary
from typing import List, Optional
from datetime import datetime

class EmotionDiaryService:
    @staticmethod
    def create_entry(
        db: Session,
        user_id: int,
        entry_data: dict
    ) -> EmotionDiary:
        """Criar entrada no diário"""
        entry = EmotionDiary(user_id=user_id, **entry_data)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_entries(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        emotion: Optional[str] = None
    ) -> List[EmotionDiary]:
        """Obter entradas do diário"""
        query = db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id
        )
        
        if start_date:
            query = query.filter(EmotionDiary.date >= start_date)
        
        if end_date:
            query = query.filter(EmotionDiary.date <= end_date)
        
        if emotion:
            query = query.filter(EmotionDiary.emotion == emotion)
        
        return query.order_by(EmotionDiary.date.desc()).all()
    
    @staticmethod
    def get_entry_by_id(
        db: Session,
        entry_id: int,
        user_id: int
    ) -> Optional[EmotionDiary]:
        """Obter entrada por ID"""
        return db.query(EmotionDiary).filter(
            EmotionDiary.id == entry_id,
            EmotionDiary.user_id == user_id
        ).first()
    
    @staticmethod
    def update_entry(
        db: Session,
        entry: EmotionDiary,
        update_data: dict
    ) -> EmotionDiary:
        """Atualizar entrada"""
        for field, value in update_data.items():
            setattr(entry, field, value)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def delete_entry(db: Session, entry_id: int, user_id: int) -> bool:
        """Deletar entrada"""
        entry = db.query(EmotionDiary).filter(
            EmotionDiary.id == entry_id,
            EmotionDiary.user_id == user_id
        ).first()
        
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    @staticmethod
    def get_stats(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Obter estatísticas do diário"""
        query = db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id
        )
        
        if start_date:
            query = query.filter(EmotionDiary.date >= start_date)
        
        if end_date:
            query = query.filter(EmotionDiary.date <= end_date)
        
        # Estatísticas por emoção
        emotion_stats = db.query(
            EmotionDiary.emotion,
            func.count(EmotionDiary.id).label('count'),
            func.avg(EmotionDiary.intensity).label('avg_intensity')
        ).filter(EmotionDiary.user_id == user_id)
        
        if start_date:
            emotion_stats = emotion_stats.filter(EmotionDiary.date >= start_date)
        if end_date:
            emotion_stats = emotion_stats.filter(EmotionDiary.date <= end_date)
        
        emotion_stats = emotion_stats.group_by(EmotionDiary.emotion).all()
        
        # Média geral de intensidade
        avg_intensity = db.query(func.avg(EmotionDiary.intensity)).filter(
            EmotionDiary.user_id == user_id
        )
        if start_date:
            avg_intensity = avg_intensity.filter(EmotionDiary.date >= start_date)
        if end_date:
            avg_intensity = avg_intensity.filter(EmotionDiary.date <= end_date)
        
        avg_intensity = avg_intensity.scalar()
        total_entries = query.count()
        
        return {
            "total_entries": total_entries,
            "average_intensity": float(avg_intensity) if avg_intensity else 0,
            "emotion_stats": [
                {
                    "emotion": stat.emotion,
                    "count": stat.count,
                    "average_intensity": float(stat.avg_intensity) if stat.avg_intensity else 0
                }
                for stat in emotion_stats
            ]
        }


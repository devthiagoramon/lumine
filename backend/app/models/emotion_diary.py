"""
EmotionDiary Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session
from typing import Optional, List
from datetime import datetime
from app.database import Base, get_db_session

class EmotionDiary(Base):
    __tablename__ = "emotion_diaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    emotion = Column(String, nullable=False)  # 'feliz', 'triste', 'ansioso', 'irritado', 'calmo', etc.
    intensity = Column(Integer, nullable=False)  # 1-10
    notes = Column(Text)
    tags = Column(String)  # Tags separadas por vírgula
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="emotion_diaries", overlaps="emotion_diaries")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_entrada: int, user_id: int) -> Optional["EmotionDiary"]:
        """Obter entrada por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id == id_entrada,
                cls.user_id == user_id
            ).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(
        cls, 
        user_id: int, 
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        emocao: Optional[str] = None
    ) -> List["EmotionDiary"]:
        """Listar entradas do diário de um usuário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.user_id == user_id)
            
            if data_inicio:
                query = query.filter(cls.date >= data_inicio)
            if data_fim:
                query = query.filter(cls.date <= data_fim)
            if emocao:
                query = query.filter(cls.emotion == emocao)
            
            return query.order_by(cls.date.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def obter_estatisticas(
        cls,
        user_id: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> dict:
        """Obter estatísticas do diário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.user_id == user_id)
            
            if data_inicio:
                query = query.filter(cls.date >= data_inicio)
            if data_fim:
                query = query.filter(cls.date <= data_fim)
            
            # Estatísticas por emoção
            emotion_stats_query = db.query(
                cls.emotion,
                func.count(cls.id).label('count'),
                func.avg(cls.intensity).label('avg_intensity')
            ).filter(cls.user_id == user_id)
            
            if data_inicio:
                emotion_stats_query = emotion_stats_query.filter(cls.date >= data_inicio)
            if data_fim:
                emotion_stats_query = emotion_stats_query.filter(cls.date <= data_fim)
            
            emotion_stats = emotion_stats_query.group_by(cls.emotion).all()
            
            # Média geral de intensidade
            avg_intensity_query = db.query(func.avg(cls.intensity)).filter(cls.user_id == user_id)
            if data_inicio:
                avg_intensity_query = avg_intensity_query.filter(cls.date >= data_inicio)
            if data_fim:
                avg_intensity_query = avg_intensity_query.filter(cls.date <= data_fim)
            
            avg_intensity = avg_intensity_query.scalar()
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
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "EmotionDiary":
        """Criar nova entrada no diário"""
        db = get_db_session()
        try:
            entrada = cls(**kwargs)
            db.add(entrada)
            db.commit()
            db.refresh(entrada)
            return entrada
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "EmotionDiary":
        """Atualizar entrada"""
        db = get_db_session()
        try:
            entrada = db.query(EmotionDiary).filter(EmotionDiary.id == self.id).first()
            if not entrada:
                raise ValueError("Entrada não encontrada")
            
            for key, value in kwargs.items():
                if hasattr(entrada, key):
                    setattr(entrada, key, value)
            db.commit()
            db.refresh(entrada)
            return entrada
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar entrada"""
        db = get_db_session()
        try:
            entrada = db.query(EmotionDiary).filter(EmotionDiary.id == self.id).first()
            if entrada:
                db.delete(entrada)
                db.commit()
        finally:
            db.close()


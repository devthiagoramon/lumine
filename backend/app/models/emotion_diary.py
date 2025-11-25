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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    data = Column("date", DateTime(timezone=True), nullable=False)
    emocao = Column("emotion", String, nullable=False)  # 'feliz', 'triste', 'ansioso', 'irritado', 'calmo', etc.
    intensidade = Column("intensity", Integer, nullable=False)  # 1-10
    notas = Column("notes", Text)
    tags = Column(String)  # Tags separadas por vírgula
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario], back_populates="emotion_diaries", overlaps="emotion_diaries")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_entrada: int, id_usuario: int) -> Optional["EmotionDiary"]:
        """Obter entrada por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id == id_entrada,
                cls.id_usuario == id_usuario
            ).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(
        cls, 
        id_usuario: int, 
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        emocao: Optional[str] = None
    ) -> List["EmotionDiary"]:
        """Listar entradas do diário de um usuário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id_usuario == id_usuario)
            
            if data_inicio:
                query = query.filter(cls.data >= data_inicio)
            if data_fim:
                query = query.filter(cls.data <= data_fim)
            if emocao:
                query = query.filter(cls.emocao == emocao)
            
            return query.order_by(cls.data.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def obter_estatisticas(
        cls,
        id_usuario: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> dict:
        """Obter estatísticas do diário"""
        db = get_db_session()
        try:
            query = db.query(cls).filter(cls.id_usuario == id_usuario)
            
            if data_inicio:
                query = query.filter(cls.data >= data_inicio)
            if data_fim:
                query = query.filter(cls.data <= data_fim)
            
            # Estatísticas por emoção
            emotion_stats_query = db.query(
                cls.emocao,
                func.count(cls.id).label('count'),
                func.avg(cls.intensidade).label('avg_intensity')
            ).filter(cls.id_usuario == id_usuario)
            
            if data_inicio:
                emotion_stats_query = emotion_stats_query.filter(cls.data >= data_inicio)
            if data_fim:
                emotion_stats_query = emotion_stats_query.filter(cls.data <= data_fim)
            
            emotion_stats = emotion_stats_query.group_by(cls.emocao).all()
            
            # Média geral de intensidade
            avg_intensity_query = db.query(func.avg(cls.intensidade)).filter(cls.id_usuario == id_usuario)
            if data_inicio:
                avg_intensity_query = avg_intensity_query.filter(cls.data >= data_inicio)
            if data_fim:
                avg_intensity_query = avg_intensity_query.filter(cls.data <= data_fim)
            
            avg_intensity = avg_intensity_query.scalar()
            total_entries = query.count()
            
            return {
                "total_entries": total_entries,
                "average_intensity": float(avg_intensity) if avg_intensity else 0,
                "emotion_stats": [
                    {
                        "emotion": stat.emocao,
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


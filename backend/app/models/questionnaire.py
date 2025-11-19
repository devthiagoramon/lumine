"""
Questionnaire Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_1 = Column(Integer)  # Resposta 1-5
    question_2 = Column(Integer)
    question_3 = Column(Integer)
    question_4 = Column(Integer)
    question_5 = Column(Integer)
    question_6 = Column(Integer)
    question_7 = Column(Integer)
    question_8 = Column(Integer)
    question_9 = Column(Integer)
    question_10 = Column(Integer)
    total_score = Column(Integer)  # Soma das respostas
    recommendation = Column(Text)  # Recomendação baseada no score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="questionnaires", overlaps="questionnaires")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_questionario: int) -> Optional["Questionnaire"]:
        """Obter questionário por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id == id_questionario).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, user_id: int) -> List["Questionnaire"]:
        """Listar questionários de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.user_id == user_id).order_by(cls.created_at.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def obter_mais_recente(cls, user_id: int) -> Optional["Questionnaire"]:
        """Obter questionário mais recente de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.user_id == user_id).order_by(cls.created_at.desc()).first()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Questionnaire":
        """Criar novo questionário"""
        db = get_db_session()
        try:
            questionario = cls(**kwargs)
            db.add(questionario)
            db.commit()
            db.refresh(questionario)
            return questionario
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Questionnaire":
        """Atualizar questionário"""
        db = get_db_session()
        try:
            questionario = db.query(Questionnaire).filter(Questionnaire.id == self.id).first()
            if not questionario:
                raise ValueError("Questionário não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(questionario, key):
                    setattr(questionario, key, value)
            db.commit()
            db.refresh(questionario)
            return questionario
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar questionário"""
        db = get_db_session()
        try:
            questionario = db.query(Questionnaire).filter(Questionnaire.id == self.id).first()
            if questionario:
                db.delete(questionario)
                db.commit()
        finally:
            db.close()


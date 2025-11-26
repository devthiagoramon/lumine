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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    pergunta_1 = Column("question_1", Integer)  # Resposta 1-5
    pergunta_2 = Column("question_2", Integer)
    pergunta_3 = Column("question_3", Integer)
    pergunta_4 = Column("question_4", Integer)
    pergunta_5 = Column("question_5", Integer)
    pergunta_6 = Column("question_6", Integer)
    pergunta_7 = Column("question_7", Integer)
    pergunta_8 = Column("question_8", Integer)
    pergunta_9 = Column("question_9", Integer)
    pergunta_10 = Column("question_10", Integer)
    pontuacao_total = Column("total_score", Integer)  # Soma das respostas
    recomendacao = Column("recommendation", Text)  # Recomendação baseada no score
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario], back_populates="questionnaires", overlaps="questionnaires")
    
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
    def listar_por_usuario(cls, id_usuario: int) -> List["Questionnaire"]:
        """Listar questionários de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id_usuario == id_usuario).order_by(cls.criado_em.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def obter_mais_recente(cls, id_usuario: int) -> Optional["Questionnaire"]:
        """Obter questionário mais recente de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id_usuario == id_usuario).order_by(cls.criado_em.desc()).first()
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


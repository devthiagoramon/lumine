"""
Review Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session, joinedload
from typing import Optional, List
from app.database import Base, get_db_session

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    psychologist = relationship("Psychologist", back_populates="reviews")
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews", overlaps="reviews")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id_com_relacionamentos(cls, id_avaliacao: int) -> Optional["Review"]:
        """Obter avaliação por ID com relacionamentos"""
        db = get_db_session()
        try:
            return db.query(cls).options(joinedload(cls.user)).filter(cls.id == id_avaliacao).first()
        finally:
            db.close()
    
    @classmethod
    def listar_por_psicologo(cls, id_psicologo: int) -> List["Review"]:
        """Listar avaliações de um psicólogo"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.psychologist_id == id_psicologo).order_by(cls.created_at.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def listar_por_usuario(cls, id_usuario: int) -> List["Review"]:
        """Listar avaliações de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.user_id == id_usuario).order_by(cls.created_at.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def verificar_existente(cls, id_psicologo: int, id_usuario: int) -> Optional["Review"]:
        """Verificar se já existe avaliação do usuário para o psicólogo"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.psychologist_id == id_psicologo,
                cls.user_id == id_usuario
            ).first()
        finally:
            db.close()
    
    @classmethod
    def calcular_rating_medio(cls, id_psicologo: int) -> float:
        """Calcular rating médio de um psicólogo"""
        db = get_db_session()
        try:
            resultado = db.query(func.avg(cls.rating)).filter(
                cls.psychologist_id == id_psicologo
            ).scalar()
            return float(resultado) if resultado else 0.0
        finally:
            db.close()
    
    @classmethod
    def contar_total(cls, id_psicologo: int) -> int:
        """Contar total de avaliações de um psicólogo"""
        db = get_db_session()
        try:
            return db.query(func.count(cls.id)).filter(
                cls.psychologist_id == id_psicologo
            ).scalar()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "Review":
        """Criar nova avaliação"""
        db = get_db_session()
        try:
            avaliacao = cls(**kwargs)
            db.add(avaliacao)
            db.commit()
            db.refresh(avaliacao)
            return avaliacao
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "Review":
        """Atualizar avaliação"""
        db = get_db_session()
        try:
            avaliacao = db.query(Review).filter(Review.id == self.id).first()
            if not avaliacao:
                raise ValueError("Avaliação não encontrada")
            
            for key, value in kwargs.items():
                if hasattr(avaliacao, key):
                    setattr(avaliacao, key, value)
            db.commit()
            db.refresh(avaliacao)
            return avaliacao
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar avaliação"""
        db = get_db_session()
        try:
            avaliacao = db.query(Review).filter(Review.id == self.id).first()
            if avaliacao:
                db.delete(avaliacao)
                db.commit()
        finally:
            db.close()


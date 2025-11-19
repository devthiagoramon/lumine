"""
PsychologistPreRegistration Model
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import Optional, List
from app.database import Base, get_db_session

class PsychologistPreRegistration(Base):
    __tablename__ = "psychologist_pre_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crp = Column(String, unique=True, nullable=False)
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    consultation_price = Column(Float)
    online_consultation = Column(Boolean, default=True)
    in_person_consultation = Column(Boolean, default=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    specialty_ids = Column(String)  # JSON array de IDs
    approach_ids = Column(String)  # JSON array de IDs
    status = Column(String, default='pending')  # 'pending', 'approved', 'rejected'
    rejection_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="pre_registrations", overlaps="pre_registrations")
    
    # Métodos de acesso ao banco
    @classmethod
    def obter_por_id(cls, id_pre_cadastro: int) -> Optional["PsychologistPreRegistration"]:
        """Obter pré-cadastro por ID"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.id == id_pre_cadastro).first()
        finally:
            db.close()
    
    @classmethod
    def obter_por_usuario(cls, user_id: int) -> Optional["PsychologistPreRegistration"]:
        """Obter pré-cadastro mais recente de um usuário"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.user_id == user_id
            ).order_by(cls.created_at.desc()).first()
        finally:
            db.close()
    
    @classmethod
    def verificar_pendente(cls, user_id: int) -> Optional["PsychologistPreRegistration"]:
        """Verificar se usuário tem pré-cadastro pendente"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.user_id == user_id,
                cls.status == 'pending'
            ).order_by(cls.created_at.desc()).first()
        finally:
            db.close()
    
    @classmethod
    def verificar_crp_existente(cls, crp: str) -> Optional["PsychologistPreRegistration"]:
        """Verificar se CRP já está cadastrado"""
        db = get_db_session()
        try:
            return db.query(cls).filter(cls.crp == crp).first()
        finally:
            db.close()
    
    @classmethod
    def listar_pendentes(cls) -> List["PsychologistPreRegistration"]:
        """Listar pré-cadastros pendentes"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.status == 'pending'
            ).order_by(cls.created_at.desc()).all()
        finally:
            db.close()
    
    @classmethod
    def criar(cls, **kwargs) -> "PsychologistPreRegistration":
        """Criar novo pré-cadastro"""
        db = get_db_session()
        try:
            pre_cadastro = cls(**kwargs)
            db.add(pre_cadastro)
            db.commit()
            db.refresh(pre_cadastro)
            return pre_cadastro
        finally:
            db.close()
    
    def atualizar(self, **kwargs) -> "PsychologistPreRegistration":
        """Atualizar pré-cadastro"""
        db = get_db_session()
        try:
            pre_cadastro = db.query(PsychologistPreRegistration).filter(PsychologistPreRegistration.id == self.id).first()
            if not pre_cadastro:
                raise ValueError("Pré-cadastro não encontrado")
            
            for key, value in kwargs.items():
                if hasattr(pre_cadastro, key):
                    setattr(pre_cadastro, key, value)
            db.commit()
            db.refresh(pre_cadastro)
            return pre_cadastro
        finally:
            db.close()
    
    def deletar(self) -> None:
        """Deletar pré-cadastro"""
        db = get_db_session()
        try:
            pre_cadastro = db.query(PsychologistPreRegistration).filter(PsychologistPreRegistration.id == self.id).first()
            if pre_cadastro:
                db.delete(pre_cadastro)
                db.commit()
        finally:
            db.close()


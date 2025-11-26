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
    id_usuario = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    crp = Column(String, unique=True, nullable=False)
    biografia = Column("bio", Text)
    anos_experiencia = Column("experience_years", Integer, default=0)
    preco_consulta = Column("consultation_price", Float)
    consulta_online = Column("online_consultation", Boolean, default=True)
    consulta_presencial = Column("in_person_consultation", Boolean, default=False)
    endereco = Column("address", String)
    cidade = Column("city", String)
    estado = Column("state", String)
    cep = Column("zip_code", String)
    ids_especialidades = Column("specialty_ids", String)  # JSON array de IDs
    ids_abordagens = Column("approach_ids", String)  # JSON array de IDs
    status = Column(String, default='pending')  # 'pending', 'approved', 'rejected'
    motivo_recusa = Column("rejection_reason", Text)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[id_usuario], back_populates="pre_registrations", overlaps="pre_registrations")
    
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
                cls.id_usuario == user_id
            ).order_by(cls.criado_em.desc()).first()
        finally:
            db.close()
    
    @classmethod
    def verificar_pendente(cls, user_id: int) -> Optional["PsychologistPreRegistration"]:
        """Verificar se usuário tem pré-cadastro pendente"""
        db = get_db_session()
        try:
            return db.query(cls).filter(
                cls.id_usuario == user_id,
                cls.status == 'pending'
            ).order_by(cls.criado_em.desc()).first()
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
            ).order_by(cls.criado_em.desc()).all()
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


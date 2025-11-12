"""
Service para gerenciar psicólogos
"""
from sqlalchemy.orm import Session, joinedload
from app.models.psychologist import Psychologist
from app.models.specialty import Specialty
from app.models.approach import Approach
from typing import Optional, List

class PsychologistService:
    @staticmethod
    def get_psychologist_by_id(
        db: Session,
        psychologist_id: int,
        load_relationships: bool = True
    ) -> Optional[Psychologist]:
        """Obter psicólogo por ID"""
        query = db.query(Psychologist)
        if load_relationships:
            query = query.options(
                joinedload(Psychologist.user),
                joinedload(Psychologist.specialties),
                joinedload(Psychologist.approaches)
            )
        return query.filter(Psychologist.id == psychologist_id).first()
    
    @staticmethod
    def get_psychologist_by_user_id(
        db: Session,
        user_id: int,
        load_relationships: bool = True
    ) -> Optional[Psychologist]:
        """Obter psicólogo por user_id"""
        query = db.query(Psychologist)
        if load_relationships:
            query = query.options(
                joinedload(Psychologist.user),
                joinedload(Psychologist.specialties),
                joinedload(Psychologist.approaches)
            )
        return query.filter(Psychologist.user_id == user_id).first()
    
    @staticmethod
    def create_psychologist(
        db: Session,
        user_id: int,
        psychologist_data: dict,
        specialty_ids: List[int] = None,
        approach_ids: List[int] = None
    ) -> Psychologist:
        """Criar perfil de psicólogo"""
        psychologist = Psychologist(user_id=user_id, **psychologist_data)
        db.add(psychologist)
        db.flush()
        
        # Adicionar especialidades
        if specialty_ids:
            specialties = db.query(Specialty).filter(Specialty.id.in_(specialty_ids)).all()
            psychologist.specialties = specialties
        
        # Adicionar abordagens
        if approach_ids:
            approaches = db.query(Approach).filter(Approach.id.in_(approach_ids)).all()
            psychologist.approaches = approaches
        
        db.commit()
        db.refresh(psychologist)
        return psychologist
    
    @staticmethod
    def update_psychologist(
        db: Session,
        psychologist: Psychologist,
        update_data: dict,
        specialty_ids: Optional[List[int]] = None,
        approach_ids: Optional[List[int]] = None
    ) -> Psychologist:
        """Atualizar perfil de psicólogo"""
        for field, value in update_data.items():
            setattr(psychologist, field, value)
        
        # Atualizar especialidades
        if specialty_ids is not None:
            specialties = db.query(Specialty).filter(Specialty.id.in_(specialty_ids)).all()
            psychologist.specialties = specialties
        
        # Atualizar abordagens
        if approach_ids is not None:
            approaches = db.query(Approach).filter(Approach.id.in_(approach_ids)).all()
            psychologist.approaches = approaches
        
        db.commit()
        db.refresh(psychologist)
        return psychologist
    
    @staticmethod
    def list_psychologists(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        load_relationships: bool = True
    ) -> List[Psychologist]:
        """Listar psicólogos"""
        query = db.query(Psychologist)
        if load_relationships:
            query = query.options(
                joinedload(Psychologist.user),
                joinedload(Psychologist.specialties),
                joinedload(Psychologist.approaches)
            )
        return query.offset(skip).limit(limit).all()


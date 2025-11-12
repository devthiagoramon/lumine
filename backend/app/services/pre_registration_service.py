"""
Service para gerenciar pré-cadastro de psicólogos
"""
from sqlalchemy.orm import Session
from app.models.psychologist_pre_registration import PsychologistPreRegistration
from app.models.psychologist import Psychologist
from app.models.specialty import Specialty
from app.models.approach import Approach
import json
from typing import Optional, List

class PreRegistrationService:
    @staticmethod
    def create_pre_registration(
        db: Session,
        user_id: int,
        pre_registration_data: dict,
        specialty_ids: List[int] = None,
        approach_ids: List[int] = None
    ) -> PsychologistPreRegistration:
        """Criar pré-cadastro"""
        pre_reg = PsychologistPreRegistration(
            user_id=user_id,
            specialty_ids=json.dumps(specialty_ids) if specialty_ids else "[]",
            approach_ids=json.dumps(approach_ids) if approach_ids else "[]",
            **pre_registration_data
        )
        db.add(pre_reg)
        db.commit()
        db.refresh(pre_reg)
        return pre_reg
    
    @staticmethod
    def get_pre_registration_by_user_id(
        db: Session,
        user_id: int
    ) -> Optional[PsychologistPreRegistration]:
        """Obter pré-cadastro por user_id"""
        return db.query(PsychologistPreRegistration).filter(
            PsychologistPreRegistration.user_id == user_id
        ).order_by(PsychologistPreRegistration.created_at.desc()).first()
    
    @staticmethod
    def approve_pre_registration(
        db: Session,
        pre_registration_id: int
    ) -> Psychologist:
        """Aprovar pré-cadastro e criar perfil de psicólogo"""
        pre_reg = db.query(PsychologistPreRegistration).filter(
            PsychologistPreRegistration.id == pre_registration_id
        ).first()
        
        if not pre_reg or pre_reg.status != 'pending':
            return None
        
        # Parse specialty_ids e approach_ids
        specialty_ids = json.loads(pre_reg.specialty_ids) if pre_reg.specialty_ids else []
        approach_ids = json.loads(pre_reg.approach_ids) if pre_reg.approach_ids else []
        
        # Criar perfil de psicólogo
        psychologist = Psychologist(
            user_id=pre_reg.user_id,
            crp=pre_reg.crp,
            bio=pre_reg.bio,
            experience_years=pre_reg.experience_years,
            consultation_price=pre_reg.consultation_price,
            online_consultation=pre_reg.online_consultation,
            in_person_consultation=pre_reg.in_person_consultation,
            address=pre_reg.address,
            city=pre_reg.city,
            state=pre_reg.state,
            zip_code=pre_reg.zip_code,
            is_verified=False
        )
        db.add(psychologist)
        db.flush()
        
        # Adicionar especialidades e abordagens
        if specialty_ids:
            specialties = db.query(Specialty).filter(Specialty.id.in_(specialty_ids)).all()
            psychologist.specialties = specialties
        
        if approach_ids:
            approaches = db.query(Approach).filter(Approach.id.in_(approach_ids)).all()
            psychologist.approaches = approaches
        
        # Atualizar status do pré-cadastro
        pre_reg.status = 'approved'
        db.commit()
        db.refresh(psychologist)
        
        return psychologist
    
    @staticmethod
    def reject_pre_registration(
        db: Session,
        pre_registration_id: int,
        rejection_reason: str
    ) -> PsychologistPreRegistration:
        """Rejeitar pré-cadastro"""
        pre_reg = db.query(PsychologistPreRegistration).filter(
            PsychologistPreRegistration.id == pre_registration_id
        ).first()
        
        if pre_reg:
            pre_reg.status = 'rejected'
            pre_reg.rejection_reason = rejection_reason
            db.commit()
            db.refresh(pre_reg)
        
        return pre_reg


"""
Service para gerenciar disponibilidade de psicólogos
"""
from sqlalchemy.orm import Session
from app.models.psychologist_availability import PsychologistAvailability
from typing import List, Optional

class AvailabilityService:
    @staticmethod
    def create_availability(
        db: Session,
        psychologist_id: int,
        availability_data: dict
    ) -> PsychologistAvailability:
        """Criar horário de disponibilidade"""
        availability = PsychologistAvailability(
            psychologist_id=psychologist_id,
            **availability_data
        )
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability
    
    @staticmethod
    def get_availability_by_psychologist(
        db: Session,
        psychologist_id: int,
        only_available: bool = False
    ) -> List[PsychologistAvailability]:
        """Obter horários de disponibilidade do psicólogo"""
        query = db.query(PsychologistAvailability).filter(
            PsychologistAvailability.psychologist_id == psychologist_id
        )
        
        if only_available:
            query = query.filter(PsychologistAvailability.is_available == True)
        
        return query.order_by(PsychologistAvailability.day_of_week).all()
    
    @staticmethod
    def get_availability_by_id(
        db: Session,
        availability_id: int,
        psychologist_id: int
    ) -> Optional[PsychologistAvailability]:
        """Obter disponibilidade por ID"""
        return db.query(PsychologistAvailability).filter(
            PsychologistAvailability.id == availability_id,
            PsychologistAvailability.psychologist_id == psychologist_id
        ).first()
    
    @staticmethod
    def update_availability(
        db: Session,
        availability: PsychologistAvailability,
        update_data: dict
    ) -> PsychologistAvailability:
        """Atualizar disponibilidade"""
        for field, value in update_data.items():
            setattr(availability, field, value)
        db.commit()
        db.refresh(availability)
        return availability
    
    @staticmethod
    def delete_availability(
        db: Session,
        availability_id: int,
        psychologist_id: int
    ) -> bool:
        """Deletar disponibilidade"""
        availability = db.query(PsychologistAvailability).filter(
            PsychologistAvailability.id == availability_id,
            PsychologistAvailability.psychologist_id == psychologist_id
        ).first()
        
        if not availability:
            return False
        
        db.delete(availability)
        db.commit()
        return True


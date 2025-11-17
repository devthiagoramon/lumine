"""
Service para gerenciar disponibilidade de psicólogos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from app.models.psychologist_availability import PsychologistAvailability
from app.models.appointment import Appointment
from typing import List, Optional
from datetime import datetime, date, timedelta, time as dt_time
from calendar import day_name

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
    
    @staticmethod
    def get_available_slots(
        db: Session,
        psychologist_id: int,
        start_date: date,
        end_date: date,
        appointment_type: str = "online"
    ) -> List[dict]:
        """
        Obter horários disponíveis para agendamento em um período
        Retorna lista de slots disponíveis considerando:
        - Disponibilidade semanal do psicólogo
        - Agendamentos já existentes
        """
        # Obter disponibilidade semanal do psicólogo
        weekly_availability = AvailabilityService.get_availability_by_psychologist(
            db=db,
            psychologist_id=psychologist_id,
            only_available=True
        )
        
        if not weekly_availability:
            return []
        
        # Obter agendamentos confirmados/pendentes no período
        appointments = db.query(Appointment).filter(
            Appointment.psychologist_id == psychologist_id,
            Appointment.appointment_date >= datetime.combine(start_date, dt_time.min),
            Appointment.appointment_date <= datetime.combine(end_date, dt_time.max),
            Appointment.status.in_(['pending', 'confirmed'])
        ).all()
        
        # Converter agendamentos para set de (date, time) para busca rápida
        booked_slots = set()
        for apt in appointments:
            apt_date = apt.appointment_date.date()
            apt_time = apt.appointment_date.time()
            booked_slots.add((apt_date, apt_time))
        
        # Gerar slots disponíveis
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            day_of_week = current_date.weekday()  # 0=Segunda, 6=Domingo
            
            # Encontrar disponibilidade para este dia da semana
            day_availability = [
                av for av in weekly_availability
                if av.day_of_week == day_of_week
            ]
            
            for av in day_availability:
                # Parse dos horários
                start_time = datetime.strptime(av.start_time, "%H:%M").time()
                end_time = datetime.strptime(av.end_time, "%H:%M").time()
                
                # Gerar slots de 1 hora
                current_time = start_time
                
                while current_time < end_time:
                    # Calcular próximo horário (1 hora depois)
                    current_datetime = datetime.combine(current_date, current_time)
                    next_datetime = current_datetime + timedelta(hours=1)
                    next_time = next_datetime.time()
                    
                    # Verificar se o próximo horário não ultrapassa o fim
                    if next_time > end_time:
                        break
                    
                    # Verificar se o slot não está ocupado
                    slot_key = (current_date, current_time)
                    if slot_key not in booked_slots:
                        # Verificar se não é no passado
                        slot_datetime = datetime.combine(current_date, current_time)
                        from datetime import timezone
                        if slot_datetime.tzinfo is None:
                            slot_datetime = slot_datetime.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        if slot_datetime > now:
                            available_slots.append({
                                "date": current_date.isoformat(),
                                "time": current_time.strftime("%H:%M"),
                                "datetime": slot_datetime.isoformat(),
                                "available": True
                            })
                    
                    current_time = next_time
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    @staticmethod
    def get_available_dates(
        db: Session,
        psychologist_id: int,
        start_date: date,
        end_date: date,
        appointment_type: str = "online"
    ) -> List[dict]:
        """
        Obter datas com horários disponíveis (para calendário)
        Retorna lista de datas com contagem de horários disponíveis
        """
        slots = AvailabilityService.get_available_slots(
            db=db,
            psychologist_id=psychologist_id,
            start_date=start_date,
            end_date=end_date,
            appointment_type=appointment_type
        )
        
        # Agrupar por data
        dates_dict = {}
        for slot in slots:
            slot_date = slot["date"]
            if slot_date not in dates_dict:
                dates_dict[slot_date] = {
                    "date": slot_date,
                    "available_slots": [],
                    "count": 0
                }
            dates_dict[slot_date]["available_slots"].append(slot["time"])
            dates_dict[slot_date]["count"] += 1
        
        return list(dates_dict.values())

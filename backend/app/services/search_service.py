"""
Service para gerenciar buscas
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.psychologist import Psychologist
from app.models.user import User
from app.models.specialty import Specialty
from app.models.approach import Approach
from typing import List, Optional

class SearchService:
    @staticmethod
    def search_psychologists(
        db: Session,
        query: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        specialty_ids: Optional[List[int]] = None,
        approach_ids: Optional[List[int]] = None,
        online_consultation: Optional[bool] = None,
        in_person_consultation: Optional[bool] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        min_experience: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Buscar psicólogos com filtros"""
        q = db.query(Psychologist)
        
        # Filtro por busca textual
        if query:
            search_term = f"%{query}%"
            q = q.join(User).filter(
                or_(
                    User.full_name.ilike(search_term),
                    Psychologist.bio.ilike(search_term),
                    Psychologist.crp.ilike(search_term)
                )
            )
        
        # Filtro por cidade
        if city:
            q = q.filter(Psychologist.city.ilike(f"%{city}%"))
        
        # Filtro por estado
        if state:
            q = q.filter(Psychologist.state.ilike(f"%{state}%"))
        
        # Filtro por especialidades
        if specialty_ids:
            q = q.join(Psychologist.specialties).filter(
                Specialty.id.in_(specialty_ids)
            )
        
        # Filtro por abordagens
        if approach_ids:
            q = q.join(Psychologist.approaches).filter(
                Approach.id.in_(approach_ids)
            )
        
        # Aplicar distinct se houver joins
        if specialty_ids or approach_ids:
            q = q.distinct()
        
        # Filtro por tipo de consulta
        if online_consultation is not None:
            q = q.filter(Psychologist.online_consultation == online_consultation)
        
        if in_person_consultation is not None:
            q = q.filter(Psychologist.in_person_consultation == in_person_consultation)
        
        # Filtro por rating mínimo
        if min_rating is not None:
            q = q.filter(Psychologist.rating >= min_rating)
        
        # Filtro por preço máximo
        if max_price is not None:
            q = q.filter(
                or_(
                    Psychologist.consultation_price <= max_price,
                    Psychologist.consultation_price.is_(None)
                )
            )
        
        # Filtro por experiência mínima
        if min_experience is not None:
            q = q.filter(Psychologist.experience_years >= min_experience)
        
        # Contar total
        total = q.count()
        
        # Paginação
        skip = (page - 1) * page_size
        psychologists = q.options(
            joinedload(Psychologist.user),
            joinedload(Psychologist.specialties),
            joinedload(Psychologist.approaches)
        ).order_by(
            Psychologist.rating.desc(),
            Psychologist.total_reviews.desc()
        ).offset(skip).limit(page_size).all()
        
        return {
            "psychologists": psychologists,
            "total": total,
            "page": page,
            "page_size": page_size
        }


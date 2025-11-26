"""
Schemas package - Todos os schemas Pydantic (Views)
"""
from app.schemas.autenticacao import Token, TokenData, UserLogin, UserCreate, UserResponse
from app.schemas.especialidade import SpecialtyBase, SpecialtyResponse
from app.schemas.abordagem import ApproachBase, ApproachResponse
from app.schemas.psicologo import (
    PsychologistBase, PsychologistCreate, PsychologistUpdate,
    PsychologistResponse, PsychologistListItem
)
from app.schemas.busca import SearchFilters, SearchResponse
from app.schemas.avaliacao import ReviewCreate, ReviewResponse
from app.schemas.agendamento import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.schemas.favorito import FavoriteResponse
from app.schemas.forum import (
    ForumPostCreate, ForumPostUpdate, ForumPostResponse,
    ForumCommentCreate, ForumCommentResponse
)
from app.schemas.diario_emocional import (
    EmotionDiaryCreate, EmotionDiaryUpdate, EmotionDiaryResponse
)
from app.schemas.pagamento import PaymentCreate, PaymentResponse
from app.schemas.metodo_pagamento import (
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse
)
from app.schemas.disponibilidade import (
    PsychologistAvailabilityCreate, PsychologistAvailabilityUpdate,
    PsychologistAvailabilityResponse
)
from app.schemas.notificacao import NotificationResponse, NotificationUpdate
from app.schemas.questionario import QuestionnaireCreate, QuestionnaireResponse
from app.schemas.pre_registro import (
    PsychologistPreRegistrationCreate, PsychologistPreRegistrationResponse
)
from app.schemas.saque import WithdrawalCreate, WithdrawalResponse

__all__ = [
    "Token", "TokenData", "UserLogin", "UserCreate", "UserResponse",
    "SpecialtyBase", "SpecialtyResponse",
    "ApproachBase", "ApproachResponse",
    "PsychologistBase", "PsychologistCreate", "PsychologistUpdate",
    "PsychologistResponse", "PsychologistListItem",
    "SearchFilters", "SearchResponse",
    "ReviewCreate", "ReviewResponse",
    "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse",
    "FavoriteResponse",
    "ForumPostCreate", "ForumPostUpdate", "ForumPostResponse",
    "ForumCommentCreate", "ForumCommentResponse",
    "EmotionDiaryCreate", "EmotionDiaryUpdate", "EmotionDiaryResponse",
    "PaymentCreate", "PaymentResponse",
    "PaymentMethodCreate", "PaymentMethodUpdate", "PaymentMethodResponse",
    "PsychologistAvailabilityCreate", "PsychologistAvailabilityUpdate",
    "PsychologistAvailabilityResponse",
    "NotificationResponse", "NotificationUpdate",
    "QuestionnaireCreate", "QuestionnaireResponse",
    "PsychologistPreRegistrationCreate", "PsychologistPreRegistrationResponse",
    "WithdrawalCreate", "WithdrawalResponse",
]


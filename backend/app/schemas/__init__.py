"""
Schemas package - Todos os schemas Pydantic (Views)
"""
from app.schemas.auth import Token, TokenData, UserLogin, UserCreate, UserResponse
from app.schemas.specialty import SpecialtyBase, SpecialtyResponse
from app.schemas.approach import ApproachBase, ApproachResponse
from app.schemas.psychologist import (
    PsychologistBase, PsychologistCreate, PsychologistUpdate,
    PsychologistResponse, PsychologistListItem
)
from app.schemas.search import SearchFilters, SearchResponse
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.schemas.favorite import FavoriteResponse
from app.schemas.forum import (
    ForumPostCreate, ForumPostUpdate, ForumPostResponse,
    ForumCommentCreate, ForumCommentResponse
)
from app.schemas.emotion_diary import (
    EmotionDiaryCreate, EmotionDiaryUpdate, EmotionDiaryResponse
)
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.availability import (
    PsychologistAvailabilityCreate, PsychologistAvailabilityUpdate,
    PsychologistAvailabilityResponse
)
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireResponse
from app.schemas.pre_registration import (
    PsychologistPreRegistrationCreate, PsychologistPreRegistrationResponse
)
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalResponse

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
    "PsychologistAvailabilityCreate", "PsychologistAvailabilityUpdate",
    "PsychologistAvailabilityResponse",
    "NotificationResponse", "NotificationUpdate",
    "QuestionnaireCreate", "QuestionnaireResponse",
    "PsychologistPreRegistrationCreate", "PsychologistPreRegistrationResponse",
    "WithdrawalCreate", "WithdrawalResponse",
]


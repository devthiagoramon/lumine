"""
Models package - Todos os modelos SQLAlchemy
"""
from app.models.association_tables import favorites, psychologist_specialties, psychologist_approaches
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.specialty import Specialty
from app.models.approach import Approach
from app.models.review import Review
from app.models.appointment import Appointment
from app.models.forum_post import ForumPost
from app.models.forum_comment import ForumComment
from app.models.emotion_diary import EmotionDiary
from app.models.payment import Payment
from app.models.psychologist_availability import PsychologistAvailability
from app.models.notification import Notification
from app.models.questionnaire import Questionnaire
from app.models.psychologist_pre_registration import PsychologistPreRegistration
from app.models.withdrawal import Withdrawal

__all__ = [
    "favorites",
    "psychologist_specialties",
    "psychologist_approaches",
    "User",
    "Psychologist",
    "Specialty",
    "Approach",
    "Review",
    "Appointment",
    "ForumPost",
    "ForumComment",
    "EmotionDiary",
    "Payment",
    "PsychologistAvailability",
    "Notification",
    "Questionnaire",
    "PsychologistPreRegistration",
    "Withdrawal",
]


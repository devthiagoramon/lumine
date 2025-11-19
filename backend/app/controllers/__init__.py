"""
Controllers package - Camada de controle (endpoints da API)
"""
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.psychologist_controller import router as psychologist_router
from app.controllers.search_controller import router as search_router
from app.controllers.review_controller import router as review_router
from app.controllers.appointment_controller import router as appointment_router
from app.controllers.favorite_controller import router as favorite_router
from app.controllers.forum_controller import router as forum_router
from app.controllers.emotion_diary_controller import router as emotion_diary_router
from app.controllers.payment_controller import router as payment_router
from app.controllers.admin_controller import router as admin_router
from app.controllers.availability_controller import router as availability_router
from app.controllers.notification_controller import router as notification_router
from app.controllers.questionnaire_controller import router as questionnaire_router
from app.controllers.pre_registration_controller import router as pre_registration_router
from app.controllers.withdrawal_controller import router as withdrawal_router
from app.controllers.treatment_map_controller import router as treatment_map_router

__all__ = [
    "auth_router",
    "user_router",
    "psychologist_router",
    "search_router",
    "review_router",
    "appointment_router",
    "favorite_router",
    "forum_router",
    "emotion_diary_router",
    "payment_router",
    "admin_router",
    "availability_router",
    "notification_router",
    "questionnaire_router",
    "pre_registration_router",
    "withdrawal_router",
    "treatment_map_router",
]


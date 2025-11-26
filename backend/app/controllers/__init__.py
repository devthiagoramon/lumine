"""
Controllers package - Camada de controle (endpoints da API)
"""
from app.controllers.autenticacao_controller import router as auth_router
from app.controllers.usuario_controller import router as user_router
from app.controllers.psicologo_controller import router as psychologist_router
from app.controllers.busca_controller import router as search_router
from app.controllers.avaliacao_controller import router as review_router
from app.controllers.agendamento_controller import router as appointment_router
from app.controllers.favorito_controller import router as favorite_router
from app.controllers.forum_controller import router as forum_router
from app.controllers.diario_emocao_controller import router as emotion_diary_router
from app.controllers.pagamento_controller import router as payment_router
from app.controllers.metodo_pagamento_controller import router as payment_method_router
from app.controllers.admin_controller import router as admin_router
from app.controllers.disponibilidade_controller import router as availability_router
from app.controllers.notificacao_controller import router as notification_router
from app.controllers.questionario_controller import router as questionnaire_router
from app.controllers.pre_registro_controller import router as pre_registration_router
from app.controllers.saque_controller import router as withdrawal_router
from app.controllers.mapa_tratamento_controller import router as treatment_map_router

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
    "payment_method_router",
    "admin_router",
    "availability_router",
    "notification_router",
    "questionnaire_router",
    "pre_registration_router",
    "withdrawal_router",
    "treatment_map_router",
]


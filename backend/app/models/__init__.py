"""
Models package - Todos os modelos SQLAlchemy
"""
from app.models.tabelas_associacao import favorites, psychologist_specialties, psychologist_approaches
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.especialidade import Specialty
from app.models.tratamento import Approach
from app.models.avaliacao import Review
from app.models.agendamento import Appointment
from app.models.post_forum import ForumPost
from app.models.comentario_forum import ForumComment
from app.models.diario_emocional import EmotionDiary
from app.models.pagamento import Payment
from app.models.metodo_pagamento import PaymentMethod
from app.models.disponibilidade_psicologo import PsychologistAvailability
from app.models.notificacao import Notification
from app.models.questionario import Questionnaire
from app.models.pre_registro_psicologo import PsychologistPreRegistration
from app.models.saque import Withdrawal

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
    "PaymentMethod",
    "PsychologistAvailability",
    "Notification",
    "Questionnaire",
    "PsychologistPreRegistration",
    "Withdrawal",
]


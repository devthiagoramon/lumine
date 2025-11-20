from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import (
    auth_router, user_router, psychologist_router, search_router,
    review_router, appointment_router, favorite_router, forum_router,
    emotion_diary_router, payment_router, payment_method_router, admin_router, availability_router,
    notification_router, questionnaire_router, pre_registration_router,
    withdrawal_router, treatment_map_router
)
from app.database import engine, Base
from app.models import *  # Importar todos os models para criar as tabelas

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lumine API",
    description="Plataforma de conexão entre pacientes e psicólogos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Controllers (rotas)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(psychologist_router, prefix="/api/psychologists", tags=["psychologists"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(review_router, prefix="/api/reviews", tags=["reviews"])
app.include_router(appointment_router, prefix="/api/appointments", tags=["appointments"])
app.include_router(favorite_router, prefix="/api/favorites", tags=["favorites"])
app.include_router(forum_router, prefix="/api/forum", tags=["forum"])
app.include_router(emotion_diary_router, prefix="/api/emotion-diary", tags=["emotion-diary"])
app.include_router(payment_router, prefix="/api/payments", tags=["payments"])
app.include_router(payment_method_router, prefix="/api/payment-methods", tags=["payment-methods"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(availability_router, prefix="/api/availability", tags=["availability"])
app.include_router(notification_router, prefix="/api/notifications", tags=["notifications"])
app.include_router(questionnaire_router, prefix="/api/questionnaires", tags=["questionnaires"])
app.include_router(pre_registration_router, prefix="/api/pre-registration", tags=["pre-registration"])
app.include_router(withdrawal_router, prefix="/api/withdrawals", tags=["withdrawals"])
app.include_router(treatment_map_router, prefix="/api/treatment-map", tags=["treatment-map"])

@app.get("/")
async def root():
    return {"message": "Lumine API - Plataforma de conexão entre pacientes e psicólogos"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}


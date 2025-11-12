from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, psychologists, search, reviews, appointments, favorites, forum, emotion_diary, payments, admin
from app.database import engine, Base

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

# Rotas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(psychologists.router, prefix="/api/psychologists", tags=["psychologists"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(forum.router, prefix="/api/forum", tags=["forum"])
app.include_router(emotion_diary.router, prefix="/api/emotion-diary", tags=["emotion-diary"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Lumine API - Plataforma de conexão entre pacientes e psicólogos"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}


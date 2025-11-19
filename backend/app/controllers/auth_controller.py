"""
Auth Controller - Endpoints de autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app import auth
from app.schemas import UserCreate, UserResponse, Token
from app.models.user import User
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def registrar(usuario: UserCreate):
    """Registrar novo usuário"""
    # Verificar se email já existe
    usuario_existente = User.obter_por_email(usuario.email)
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Email já registrado"
        )
    
    # Criar novo usuário
    senha_hash = auth.get_password_hash(usuario.password)
    usuario_db = User.criar(
        email=usuario.email,
        hashed_password=senha_hash,
        full_name=usuario.full_name,
        phone=usuario.phone,
        is_psychologist=usuario.is_psychologist,
        is_active=True,
        is_admin=False
    )
    return usuario_db

@router.post("/login", response_model=Token)
def fazer_login(
    dados_formulario: OAuth2PasswordRequestForm = Depends()
):
    """Fazer login"""
    usuario = auth.authenticate_user(dados_formulario.username, dados_formulario.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_acesso = auth.create_access_token(
        data={"sub": usuario.email}, expires_delta=expiracao_token
    )
    return {"access_token": token_acesso, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def obter_usuario_atual(usuario_atual: User = Depends(auth.get_current_active_user)):
    """Obter usuário atual"""
    return usuario_atual


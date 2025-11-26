from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.usuario import User
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Usar bcrypt diretamente para evitar problemas com passlib
# O passlib tem problemas de compatibilidade com algumas versões do bcrypt
# Usando bcrypt diretamente, evitamos o erro "AttributeError: module 'bcrypt' has no attribute '__about__'"
USE_PASSLIB = False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password, hashed_password):
    """Verifica se a senha está correta usando bcrypt diretamente"""
    try:
        # Bcrypt tem limite de 72 bytes, truncar se necessário
        if isinstance(plain_password, str):
            password_bytes = plain_password.encode('utf-8')
        else:
            password_bytes = plain_password
        
        # Truncar se exceder 72 bytes
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Converter hashed_password para bytes se necessário
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
        
        # Usar bcrypt diretamente
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password):
    """Gera hash da senha usando bcrypt diretamente"""
    try:
        # Bcrypt tem limite de 72 bytes, garantir que não exceda
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
        else:
            password_bytes = password
        
        # Truncar se necessário (muito raro, mas por segurança)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Usar bcrypt diretamente
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception:
        # Fallback em caso de erro
        salt = bcrypt.gensalt(rounds=12)
        if isinstance(password, str):
            password = password.encode('utf-8')
        if len(password) > 72:
            password = password[:72]
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str):
    user = User.obter_por_email(email)
    if not user:
        return False
    if not verify_password(password, user.senha_hash):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = User.obter_por_email(email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.esta_ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.eh_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


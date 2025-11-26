"""
User Controller - Endpoints de usuários
"""
from fastapi import APIRouter, Depends, HTTPException
from app import auth
from app.schemas import UserResponse
from app.models.usuario import User

router = APIRouter()

@router.get("/{id_usuario}", response_model=UserResponse)
def obter_usuario(
    id_usuario: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter usuário por ID"""
    usuario = User.obter_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


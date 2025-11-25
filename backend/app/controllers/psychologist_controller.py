"""
Psychologist Controller - Endpoints de psicólogos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import auth
from app.schemas import (
    PsychologistCreate, PsychologistUpdate, PsychologistResponse, PsychologistListItem
)
from app.models.user import User
from app.models.psychologist import Psychologist

router = APIRouter()

@router.post("/", response_model=PsychologistResponse, status_code=status.HTTP_201_CREATED)
def criar_perfil_psicologo(
    psicologo: PsychologistCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar perfil de psicólogo"""
    # Verificar se usuário é psicólogo
    if not usuario_atual.eh_psicologo:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem criar perfis"
        )
    
    # Verificar se já tem perfil
    existente = Psychologist.obter_por_user_id(usuario_atual.id)
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Perfil de psicólogo já existe"
        )
    
    # Verificar se CRP já existe
    crp_existente = Psychologist.obter_por_crp(psicologo.crp)
    if crp_existente:
        raise HTTPException(
            status_code=400,
            detail="CRP já registrado"
        )
    
    # Criar perfil com relacionamentos
    dados_psicologo = psicologo.dict(exclude={"specialty_ids", "approach_ids"})
    psicologo_created = Psychologist.criar_com_relacionamentos(
        user_id=usuario_atual.id,
        specialty_ids=psicologo.specialty_ids,
        approach_ids=psicologo.approach_ids,
        **dados_psicologo
    )
    
    # Recarregar com relacionamentos
    psicologo_created = Psychologist.obter_por_id(psicologo_created.id, carregar_relacionamentos=True)
    
    return psicologo_created

@router.get("/me", response_model=PsychologistResponse)
def obter_meu_perfil(
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meu perfil de psicólogo"""
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    # Recarregar com relacionamentos
    psicologo = Psychologist.obter_por_id(psicologo.id, carregar_relacionamentos=True)
    return psicologo

@router.put("/me", response_model=PsychologistResponse)
def atualizar_meu_perfil(
    atualizacao_psicologo: PsychologistUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar meu perfil de psicólogo"""
    psicologo = Psychologist.obter_por_user_id(usuario_atual.id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    # Atualizar campos e relacionamentos
    dados_atualizacao = atualizacao_psicologo.dict(exclude_unset=True, exclude={"specialty_ids", "approach_ids"})
    psicologo_updated = psicologo.atualizar_com_relacionamentos(
        specialty_ids=atualizacao_psicologo.specialty_ids,
        approach_ids=atualizacao_psicologo.approach_ids,
        **dados_atualizacao
    )
    
    # Recarregar com relacionamentos
    psicologo_object = Psychologist.obter_por_id(psicologo_updated.id, carregar_relacionamentos=True)
    
    return psicologo_object

@router.get("/{id_psicologo}", response_model=PsychologistResponse)
def obter_psicologo(
    id_psicologo: int
):
    """Obter psicólogo por ID"""
    psicologo = Psychologist.obter_por_id(id_psicologo, carregar_relacionamentos=True)
    
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    return psicologo

@router.get("/", response_model=List[PsychologistListItem])
def listar_psicologos(
    pular: int = 0,
    limite: int = 20
):
    """Listar psicólogos"""
    psicologos = Psychologist.listar_verificados(pular=pular, limite=limite)
    return psicologos


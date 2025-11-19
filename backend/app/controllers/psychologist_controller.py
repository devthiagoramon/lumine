"""
Psychologist Controller - Endpoints de psicólogos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app import auth
from app.schemas import (
    PsychologistCreate, PsychologistUpdate, PsychologistResponse, PsychologistListItem
)
from app.models.user import User
from app.models.psychologist import Psychologist
from app.models.specialty import Specialty
from app.models.approach import Approach

router = APIRouter()

@router.post("/", response_model=PsychologistResponse, status_code=status.HTTP_201_CREATED)
def criar_perfil_psicologo(
    psicologo: PsychologistCreate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar perfil de psicólogo"""
    # Verificar se usuário é psicólogo
    if not usuario_atual.is_psychologist:
        raise HTTPException(
            status_code=403,
            detail="Apenas psicólogos podem criar perfis"
        )
    
    # Verificar se já tem perfil
    existente = Psychologist.obter_por_user_id(db, usuario_atual.id)
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Perfil de psicólogo já existe"
        )
    
    # Verificar se CRP já existe
    crp_existente = Psychologist.obter_por_crp(db, psicologo.crp)
    if crp_existente:
        raise HTTPException(
            status_code=400,
            detail="CRP já registrado"
        )
    
    # Criar perfil
    dados_psicologo = psicologo.dict(exclude={"specialty_ids", "approach_ids"})
    psicologo_db = Psychologist.criar(db, user_id=usuario_atual.id, **dados_psicologo)
    
    # Adicionar especialidades
    if psicologo.specialty_ids:
        especialidades = Specialty.obter_por_ids(db, psicologo.specialty_ids)
        psicologo_db.specialties = especialidades
    
    # Adicionar abordagens
    if psicologo.approach_ids:
        abordagens = Approach.obter_por_ids(db, psicologo.approach_ids)
        psicologo_db.approaches = abordagens
    
    db.commit()
    db.refresh(psicologo_db)
    
    # Recarregar com relacionamentos
    psicologo_db = Psychologist.obter_por_id(db, psicologo_db.id, carregar_relacionamentos=True)
    
    return psicologo_db

@router.get("/me", response_model=PsychologistResponse)
def obter_meu_perfil(
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter meu perfil de psicólogo"""
    psicologo = Psychologist.obter_por_user_id(db, usuario_atual.id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    # Recarregar com relacionamentos
    psicologo = Psychologist.obter_por_id(db, psicologo.id, carregar_relacionamentos=True)
    return psicologo

@router.put("/me", response_model=PsychologistResponse)
def atualizar_meu_perfil(
    atualizacao_psicologo: PsychologistUpdate,
    db: Session = Depends(get_db),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar meu perfil de psicólogo"""
    psicologo = Psychologist.obter_por_user_id(db, usuario_atual.id)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Perfil de psicólogo não encontrado"
        )
    
    # Atualizar campos
    dados_atualizacao = atualizacao_psicologo.dict(exclude_unset=True, exclude={"specialty_ids", "approach_ids"})
    psicologo.atualizar(db, **dados_atualizacao)
    
    # Atualizar especialidades
    if atualizacao_psicologo.specialty_ids is not None:
        especialidades = Specialty.obter_por_ids(db, atualizacao_psicologo.specialty_ids)
        psicologo.specialties = especialidades
    
    # Atualizar abordagens
    if atualizacao_psicologo.approach_ids is not None:
        abordagens = Approach.obter_por_ids(db, atualizacao_psicologo.approach_ids)
        psicologo.approaches = abordagens
    
    db.commit()
    db.refresh(psicologo)
    
    # Recarregar com relacionamentos
    psicologo_db = Psychologist.obter_por_id(db, psicologo.id, carregar_relacionamentos=True)
    
    return psicologo_db

@router.get("/{id_psicologo}", response_model=PsychologistResponse)
def obter_psicologo(
    id_psicologo: int,
    db: Session = Depends(get_db)
):
    """Obter psicólogo por ID"""
    psicologo = Psychologist.obter_por_id(db, id_psicologo, carregar_relacionamentos=True)
    if not psicologo:
        raise HTTPException(
            status_code=404,
            detail="Psicólogo não encontrado"
        )
    return psicologo

@router.get("/", response_model=List[PsychologistListItem])
def listar_psicologos(
    pular: int = 0,
    limite: int = 20,
    db: Session = Depends(get_db)
):
    """Listar psicólogos"""
    psicologos = Psychologist.listar_verificados(db, pular=pular, limite=limite)
    return psicologos


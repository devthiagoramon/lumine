"""
Psychologist Controller - Endpoints de psicólogos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from app import auth
from app.schemas import (
    PsychologistCreate, PsychologistUpdate, PsychologistResponse, PsychologistListItem
)
from app.models.usuario import User
from app.models.psicologo import Psychologist

router = APIRouter()

@router.post("/", response_model=PsychologistResponse, status_code=status.HTTP_201_CREATED)
def criar_perfil_psicologo(
    psicologo: PsychologistCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar perfil de psicólogo"""
    try:
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
        # Mapear campos do schema (inglês) para o modelo (português)
        dados_psicologo = psicologo.dict(exclude={"specialty_ids", "approach_ids"})
        dados_modelo = {
            "id_usuario": usuario_atual.id,
            "crp": dados_psicologo["crp"],
            "biografia": dados_psicologo.get("bio"),
            "anos_experiencia": dados_psicologo.get("experience_years", 0),
            "preco_consulta": dados_psicologo.get("consultation_price"),
            "consulta_online": dados_psicologo.get("online_consultation", True),
            "consulta_presencial": dados_psicologo.get("in_person_consultation", False),
            "endereco": dados_psicologo.get("address"),
            "cidade": dados_psicologo.get("city"),
            "estado": dados_psicologo.get("state"),
            "cep": dados_psicologo.get("zip_code"),
            "foto_perfil": dados_psicologo.get("profile_picture"),
        }
        psicologo_created = Psychologist.criar_com_relacionamentos(
            specialty_ids=psicologo.specialty_ids or [],
            approach_ids=psicologo.approach_ids or [],
            **dados_modelo
        )
        
        # Recarregar com relacionamentos
        psicologo_created = Psychologist.obter_por_id(psicologo_created.id, carregar_relacionamentos=True)
        
        return psicologo_created
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar perfil de psicólogo: {str(e)}"
        )

@router.get("/me")
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
    
    # Criar o objeto de resposta e serializar manualmente para garantir que use os nomes dos campos
    # (não os aliases em português)
    try:
        response_obj = PsychologistResponse.model_validate(psicologo)
        # Serializar sem aliases para garantir que o frontend receba os campos corretos
        # IMPORTANTE: serializar objetos aninhados também sem aliases
        try:
            # Tentar usar mode='json' (Pydantic v2)
            serialized = response_obj.model_dump(by_alias=False, mode='json')
        except TypeError:
            # Se mode='json' não existir (Pydantic v1), usar apenas by_alias=False
            serialized = response_obj.model_dump(by_alias=False)
        
        
        return JSONResponse(content=serialized)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao serializar resposta: {str(e)}"
        )

@router.put("/me")
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
    # IMPORTANTE: O frontend SEMPRE envia esses campos, então vamos processá-los SEMPRE
    dados_modelo = {}
    
    # Processar experience_years - SEMPRE processar (o frontend sempre envia)
    valor_experience = atualizacao_psicologo.experience_years
    if valor_experience is not None:
        dados_modelo["anos_experiencia"] = int(valor_experience)
    else:
        dados_modelo["anos_experiencia"] = 0
    
    # Processar tipos de consulta - SEMPRE processar (o frontend sempre envia)
    valor_online = atualizacao_psicologo.online_consultation
    if valor_online is not None:
        dados_modelo["consulta_online"] = bool(valor_online)
    else:
        dados_modelo["consulta_online"] = False
    
    valor_presencial = atualizacao_psicologo.in_person_consultation
    if valor_presencial is not None:
        dados_modelo["consulta_presencial"] = bool(valor_presencial)
    else:
        dados_modelo["consulta_presencial"] = False
    
    # Processar outros campos opcionais
    try:
        dados_atualizacao = atualizacao_psicologo.model_dump(exclude_unset=True, exclude={"specialty_ids", "approach_ids", "experience_years", "online_consultation", "in_person_consultation"})
    except AttributeError:
        dados_atualizacao = atualizacao_psicologo.dict(exclude_unset=True, exclude={"specialty_ids", "approach_ids", "experience_years", "online_consultation", "in_person_consultation"})
    
    if "bio" in dados_atualizacao:
        dados_modelo["biografia"] = dados_atualizacao["bio"]
    if "consultation_price" in dados_atualizacao:
        dados_modelo["preco_consulta"] = dados_atualizacao["consultation_price"]
    if "address" in dados_atualizacao:
        dados_modelo["endereco"] = dados_atualizacao["address"]
    if "city" in dados_atualizacao:
        dados_modelo["cidade"] = dados_atualizacao["city"]
    if "state" in dados_atualizacao:
        dados_modelo["estado"] = dados_atualizacao["state"]
    if "zip_code" in dados_atualizacao:
        dados_modelo["cep"] = dados_atualizacao["zip_code"]
    if "profile_picture" in dados_atualizacao:
        dados_modelo["foto_perfil"] = dados_atualizacao["profile_picture"]
    
    psicologo_updated = psicologo.atualizar_com_relacionamentos(
        specialty_ids=atualizacao_psicologo.specialty_ids,
        approach_ids=atualizacao_psicologo.approach_ids,
        **dados_modelo
    )
    
    # Recarregar com relacionamentos
    psicologo_object = Psychologist.obter_por_id(psicologo_updated.id, carregar_relacionamentos=True)
    
    # Criar o objeto de resposta e serializar manualmente para garantir que use os nomes dos campos
    # (não os aliases em português)
    try:
        response_obj = PsychologistResponse.model_validate(psicologo_object)
        # Serializar sem aliases para garantir que o frontend receba os campos corretos
        # IMPORTANTE: serializar objetos aninhados também sem aliases
        try:
            # Tentar usar mode='json' (Pydantic v2)
            serialized = response_obj.model_dump(by_alias=False, mode='json')
        except TypeError:
            # Se mode='json' não existir (Pydantic v1), usar apenas by_alias=False
            serialized = response_obj.model_dump(by_alias=False)
        
        
        return JSONResponse(content=serialized)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao serializar resposta: {str(e)}"
        )

@router.get("/{id_psicologo}")
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
    
    # Serializar manualmente para garantir que os campos sejam retornados com nomes em inglês
    try:
        # Pydantic v2
        response_obj = PsychologistResponse.model_validate(psicologo)
        serialized = response_obj.model_dump(by_alias=False, mode='json')
    except AttributeError:
        # Pydantic v1 fallback
        response_obj = PsychologistResponse.from_orm(psicologo)
        serialized = response_obj.dict(by_alias=False)
    
    return JSONResponse(content=serialized)

@router.get("/", response_model=List[PsychologistListItem])
def listar_psicologos(
    pular: int = 0,
    limite: int = 20
):
    """Listar psicólogos"""
    psicologos = Psychologist.listar_verificados(pular=pular, limite=limite)
    return psicologos


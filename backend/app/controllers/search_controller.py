"""
Search Controller - Endpoints de busca
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from app.schemas import SearchResponse, SpecialtyResponse, ApproachResponse
from app.models.specialty import Specialty
from app.models.approach import Approach
from app.models.psychologist import Psychologist

router = APIRouter()

@router.get("/psychologists", response_model=SearchResponse)
def buscar_psicologos(
    consulta: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    ids_especialidades: Optional[List[int]] = Query(None),
    ids_abordagens: Optional[List[int]] = Query(None),
    consulta_online: Optional[bool] = Query(None),
    consulta_presencial: Optional[bool] = Query(None),
    avaliacao_minima: Optional[float] = Query(None),
    preco_maximo: Optional[float] = Query(None),
    experiencia_minima: Optional[int] = Query(None),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100)
):
    """Buscar psicólogos com filtros"""
    result = Psychologist.buscar_com_filtros(
        consulta=consulta,
        cidade=cidade,
        estado=estado,
        ids_especialidades=ids_especialidades,
        ids_abordagens=ids_abordagens,
        consulta_online=consulta_online,
        consulta_presencial=consulta_presencial,
        avaliacao_minima=avaliacao_minima,
        preco_maximo=preco_maximo,
        experiencia_minima=experiencia_minima,
        pagina=pagina,
        tamanho_pagina=tamanho_pagina
    )
    return result

@router.get("/specialties", response_model=List[SpecialtyResponse])
def obter_especialidades():
    """Listar especialidades"""
    specialties = Specialty.listar_todos()
    return specialties

@router.get("/approaches", response_model=List[ApproachResponse])
def obter_abordagens():
    """Listar abordagens"""
    approaches = Approach.listar_todos()
    return approaches


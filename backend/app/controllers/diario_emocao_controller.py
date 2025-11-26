"""
Emotion Diary Controller - Endpoints de diário de emoções
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app import auth
from app.schemas import (
    EmotionDiaryCreate, EmotionDiaryUpdate, EmotionDiaryResponse
)
from app.models.usuario import User
from app.models.diario_emocional import EmotionDiary

router = APIRouter()

@router.post("/", response_model=EmotionDiaryResponse, status_code=status.HTTP_201_CREATED)
def criar_entrada(
    entrada: EmotionDiaryCreate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Criar entrada no diário"""
    # Validar intensidade
    if entrada.intensity < 1 or entrada.intensity > 10:
        raise HTTPException(
            status_code=400,
            detail="Intensidade deve estar entre 1 e 10"
        )
    
    import sys
    import traceback
    
    try:
        entrada_created = EmotionDiary.criar(
            id_usuario=usuario_atual.id,
            data=entrada.date,
            emocao=entrada.emotion,
            intensidade=entrada.intensity,
            notas=entrada.notes,
            tags=entrada.tags
        )
        
        print(f"DEBUG: Entrada criada com sucesso - ID: {entrada_created.id}", file=sys.stderr, flush=True)
        
        # Serializar manualmente para garantir que os aliases sejam usados
        from app.schemas.diario_emocional import EmotionDiaryResponse
        entrada_dict = EmotionDiaryResponse.model_validate(entrada_created).model_dump(by_alias=True, mode='json')
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content=entrada_dict, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"ERROR: Erro ao criar entrada: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar entrada: {str(e)}"
        )

@router.get("/", response_model=List[EmotionDiaryResponse])
def obter_entradas(
    data_inicio: Optional[datetime] = Query(None, alias="data_inicio"),
    data_fim: Optional[datetime] = Query(None, alias="data_fim"),
    emocao: Optional[str] = Query(None),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter entradas do diário"""
    entradas = EmotionDiary.listar_por_usuario(
        usuario_atual.id, 
        data_inicio=data_inicio, 
        data_fim=data_fim, 
        emocao=emocao
    )
    
    # Serializar manualmente para garantir que os aliases sejam usados
    try:
        from app.schemas.diario_emocional import EmotionDiaryResponse
        serialized = []
        for entrada in entradas:
            entrada_dict = EmotionDiaryResponse.model_validate(entrada).model_dump(by_alias=True, mode='json')
            serialized.append(entrada_dict)
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content=serialized)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar entradas: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        # Fallback: retornar sem serialização manual
        return entradas

@router.get("/stats")
def obter_estatisticas(
    data_inicio: Optional[datetime] = Query(None, alias="data_inicio"),
    data_fim: Optional[datetime] = Query(None, alias="data_fim"),
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter estatísticas do diário"""
    estatisticas = EmotionDiary.obter_estatisticas(
        usuario_atual.id, 
        data_inicio=data_inicio, 
        data_fim=data_fim
    )
    return estatisticas

@router.get("/{id_entrada}", response_model=EmotionDiaryResponse)
def obter_entrada(
    id_entrada: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Obter entrada por ID"""
    entrada = EmotionDiary.obter_por_id(id_entrada, usuario_atual.id)
    
    if not entrada:
        raise HTTPException(
            status_code=404,
            detail="Entrada não encontrada"
        )
    
    return entrada

@router.put("/{id_entrada}", response_model=EmotionDiaryResponse)
def atualizar_entrada(
    id_entrada: int,
    atualizacao_entrada: EmotionDiaryUpdate,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Atualizar entrada"""
    entrada = EmotionDiary.obter_por_id(id_entrada, usuario_atual.id)
    
    if not entrada:
        raise HTTPException(
            status_code=404,
            detail="Entrada não encontrada"
        )
    
    # Validar intensidade se fornecida
    if atualizacao_entrada.intensity is not None:
        if atualizacao_entrada.intensity < 1 or atualizacao_entrada.intensity > 10:
            raise HTTPException(
                status_code=400,
                detail="Intensidade deve estar entre 1 e 10"
            )
    
    # Mapear campos do schema para o modelo
    dados_atualizacao = {}
    if atualizacao_entrada.date is not None:
        dados_atualizacao['data'] = atualizacao_entrada.date
    if atualizacao_entrada.emotion is not None:
        dados_atualizacao['emocao'] = atualizacao_entrada.emotion
    if atualizacao_entrada.intensity is not None:
        dados_atualizacao['intensidade'] = atualizacao_entrada.intensity
    if atualizacao_entrada.notes is not None:
        dados_atualizacao['notas'] = atualizacao_entrada.notes
    if atualizacao_entrada.tags is not None:
        dados_atualizacao['tags'] = atualizacao_entrada.tags
    
    entrada.atualizar(**dados_atualizacao)
    
    # Recarregar entrada
    entrada = EmotionDiary.obter_por_id(id_entrada, usuario_atual.id)
    
    # Serializar manualmente
    try:
        from app.schemas.diario_emocional import EmotionDiaryResponse
        entrada_dict = EmotionDiaryResponse.model_validate(entrada).model_dump(by_alias=True, mode='json')
        from fastapi.responses import JSONResponse
        return JSONResponse(content=entrada_dict)
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: Erro ao serializar entrada atualizada: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return entrada

@router.delete("/{id_entrada}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_entrada(
    id_entrada: int,
    usuario_atual: User = Depends(auth.get_current_active_user)
):
    """Deletar entrada"""
    entrada = EmotionDiary.obter_por_id(id_entrada, usuario_atual.id)
    
    if not entrada:
        raise HTTPException(
            status_code=404,
            detail="Entrada não encontrada"
        )
    
    entrada.deletar()
    return None

@router.get("/emotions/list")
def obter_lista_emocoes():
    """Obter lista de emoções"""
    return {
        "emotions": [
            {"value": "feliz", "label": "Feliz"},
            {"value": "triste", "label": "Triste"},
            {"value": "ansioso", "label": "Ansioso"},
            {"value": "irritado", "label": "Irritado"},
            {"value": "calmo", "label": "Calmo"},
            {"value": "estressado", "label": "Estressado"},
            {"value": "motivado", "label": "Motivado"},
            {"value": "cansado", "label": "Cansado"},
            {"value": "gratidão", "label": "Gratidão"},
            {"value": "medo", "label": "Medo"},
            {"value": "raiva", "label": "Raiva"},
            {"value": "esperança", "label": "Esperança"},
            {"value": "confuso", "label": "Confuso"},
            {"value": "orgulhoso", "label": "Orgulhoso"},
            {"value": "culpado", "label": "Culpado"}
        ]
    }


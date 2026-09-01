from fastapi import APIRouter

from app.modules.anonimizacao.schemas import AnonimizacaoResponse, ExemploAnonimizacao

router = APIRouter(prefix="/api/anonimizacao", tags=["Anonimização"])


@router.get("/", response_model=AnonimizacaoResponse)
def status_anonimizacao() -> AnonimizacaoResponse:
    return AnonimizacaoResponse(
        mensagem="Módulo de anonimização em construção",
        exemplo=ExemploAnonimizacao(campo="Nome", antes="João Silva", depois="ANONIMO"),
    )

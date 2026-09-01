from fastapi import APIRouter

from app.modules.lgpd.schemas import AvaliacaoLgpdResponse

router = APIRouter(prefix="/api/lgpd", tags=["Avaliação LGPD"])


@router.get("/", response_model=AvaliacaoLgpdResponse)
def status_lgpd() -> AvaliacaoLgpdResponse:
    return AvaliacaoLgpdResponse(
        mensagem="Módulo de avaliação LGPD em construção",
        nivel_risco="Indefinido",
        dados_encontrados=[],
    )

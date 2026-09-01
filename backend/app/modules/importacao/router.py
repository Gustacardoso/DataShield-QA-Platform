from fastapi import APIRouter

from app.modules.importacao.schemas import ImportacaoStatusResponse

router = APIRouter(prefix="/api/importacao", tags=["Importação"])


@router.get("/", response_model=ImportacaoStatusResponse)
def status_importacao() -> ImportacaoStatusResponse:
    return ImportacaoStatusResponse(
        mensagem="Módulo de importação em construção",
        formatos_suportados=["csv", "xlsx", "json"],
    )

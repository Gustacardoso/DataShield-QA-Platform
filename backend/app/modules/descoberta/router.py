from fastapi import APIRouter

from app.modules.descoberta.schemas import DescobertaResponse

router = APIRouter(prefix="/api/descoberta", tags=["Descoberta de Dados Sensíveis"])


@router.get("/", response_model=DescobertaResponse)
def status_descoberta() -> DescobertaResponse:
    return DescobertaResponse(
        mensagem="Módulo de descoberta de dados sensíveis em construção",
        tipos_detectaveis=["CPF", "RG", "Telefone", "Email", "Nome", "Endereço", "Data de nascimento"],
        colunas=[],
    )

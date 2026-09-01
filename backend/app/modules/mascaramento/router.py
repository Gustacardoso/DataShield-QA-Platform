from fastapi import APIRouter

from app.modules.mascaramento.schemas import MascaramentoResponse, RegraMascaramento

router = APIRouter(prefix="/api/mascaramento", tags=["Mascaramento"])


@router.get("/", response_model=MascaramentoResponse)
def status_mascaramento() -> MascaramentoResponse:
    return MascaramentoResponse(
        mensagem="Módulo de mascaramento em construção",
        regras=[
            RegraMascaramento(tipo_dado="CPF", exemplo_antes="123.456.789-10", exemplo_depois="***.***.***-10"),
            RegraMascaramento(tipo_dado="Email", exemplo_antes="joao@email.com", exemplo_depois="j*****@email.com"),
        ],
    )

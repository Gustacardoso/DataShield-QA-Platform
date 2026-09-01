from fastapi import APIRouter

from app.modules.sinteticos.schemas import RegistroSintetico, SinteticosResponse

router = APIRouter(prefix="/api/sinteticos", tags=["Dados Sintéticos"])


@router.get("/", response_model=SinteticosResponse)
def status_sinteticos() -> SinteticosResponse:
    return SinteticosResponse(
        mensagem="Módulo de geração de dados sintéticos em construção",
        exemplo=RegistroSintetico(nome="Ana Lima", cpf="111.222.333-44", email="ana@teste.com"),
    )

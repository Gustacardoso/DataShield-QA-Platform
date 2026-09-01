from pydantic import BaseModel


class AvaliacaoLgpdResponse(BaseModel):
    mensagem: str
    nivel_risco: str
    dados_encontrados: list[str]

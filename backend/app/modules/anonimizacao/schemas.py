from pydantic import BaseModel


class AplicarAnonimizacaoRequest(BaseModel):
    colunas: list[str] | None = None


class AnonimizacaoResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    colunas_anonimizadas: list[str]
    preview: list[dict]

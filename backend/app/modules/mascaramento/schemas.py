from pydantic import BaseModel


class AplicarMascaramentoRequest(BaseModel):
    colunas: list[str] | None = None


class MascaramentoResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    colunas_mascaradas: list[str]
    preview: list[dict]

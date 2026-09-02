from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ColunaClassificadaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome_coluna: str
    sensivel: bool
    tipo_dado: str | None


class DescobertaResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    colunas: list[ColunaClassificadaResponse]
    criado_em: datetime

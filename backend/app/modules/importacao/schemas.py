from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArquivoImportadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_arquivo: str
    formato: str
    num_linhas: int
    colunas: list[str]
    criado_em: datetime


class ArquivoImportadoDetalhe(ArquivoImportadoResponse):
    preview: list[dict]

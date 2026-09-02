from pydantic import BaseModel


class DadoEncontrado(BaseModel):
    coluna: str
    tipo_dado: str | None
    quantidade_encontrada: int
    tratado: bool


class AvaliacaoLgpdResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    nivel_risco: str
    total_colunas_sensiveis: int
    colunas_tratadas: int
    dados_encontrados: list[DadoEncontrado]

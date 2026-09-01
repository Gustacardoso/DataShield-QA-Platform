from pydantic import BaseModel


class ColunaAnalisada(BaseModel):
    coluna: str
    tipo_dado: str
    sensivel: bool


class DescobertaResponse(BaseModel):
    mensagem: str
    tipos_detectaveis: list[str]
    colunas: list[ColunaAnalisada]

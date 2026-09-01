from pydantic import BaseModel


class ImportacaoStatusResponse(BaseModel):
    mensagem: str
    formatos_suportados: list[str]

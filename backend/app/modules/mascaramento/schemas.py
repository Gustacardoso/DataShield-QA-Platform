from pydantic import BaseModel


class RegraMascaramento(BaseModel):
    tipo_dado: str
    exemplo_antes: str
    exemplo_depois: str


class MascaramentoResponse(BaseModel):
    mensagem: str
    regras: list[RegraMascaramento]

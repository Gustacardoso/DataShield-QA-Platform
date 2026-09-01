from pydantic import BaseModel


class ExemploAnonimizacao(BaseModel):
    campo: str
    antes: str
    depois: str


class AnonimizacaoResponse(BaseModel):
    mensagem: str
    exemplo: ExemploAnonimizacao

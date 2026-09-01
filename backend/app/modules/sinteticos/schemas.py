from pydantic import BaseModel


class RegistroSintetico(BaseModel):
    nome: str
    cpf: str
    email: str


class SinteticosResponse(BaseModel):
    mensagem: str
    exemplo: RegistroSintetico

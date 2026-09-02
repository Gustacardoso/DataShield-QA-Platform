from pydantic import BaseModel, Field


class GerarSinteticosRequest(BaseModel):
    num_linhas: int = Field(default=100, gt=0, le=50_000)


class SinteticosResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    num_linhas: int
    preview: list[dict]

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    arquivos_processados: int
    dados_mascarados: int
    dados_anonimizados: int
    dados_sinteticos_gerados: int
    indice_conformidade_lgpd: float

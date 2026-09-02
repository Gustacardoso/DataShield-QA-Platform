from app.models.coluna_classificada import ColunaClassificada


def calcular_nivel_risco(colunas: list[ColunaClassificada]) -> str:
    sensiveis = [c for c in colunas if c.sensivel]
    if not sensiveis:
        return "Baixo"

    tratadas = sum(1 for c in sensiveis if c.mascarada or c.anonimizada)
    if tratadas == len(sensiveis):
        return "Baixo"
    if tratadas == 0:
        return "Alto"
    return "Médio"

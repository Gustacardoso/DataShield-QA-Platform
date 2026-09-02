import pandas as pd

PLACEHOLDER = "ANONIMO"


def anonimizar_valor(valor: object) -> object:
    return valor if pd.isna(valor) else PLACEHOLDER


def anonimizar_dataframe(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    resultado = df.copy()
    for coluna in colunas:
        if coluna not in resultado.columns:
            continue
        resultado[coluna] = resultado[coluna].map(anonimizar_valor)
    return resultado

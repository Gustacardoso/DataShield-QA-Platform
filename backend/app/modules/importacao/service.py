import json
from pathlib import Path

import pandas as pd

FORMATOS_SUPORTADOS = {"csv", "txt", "xlsx", "xls", "json"}


def formato_da_extensao(nome_arquivo: str) -> str:
    extensao = Path(nome_arquivo).suffix.lower().removeprefix(".")
    if extensao not in FORMATOS_SUPORTADOS:
        raise ValueError(f"Formato '{extensao}' não suportado. Use: {', '.join(sorted(FORMATOS_SUPORTADOS))}.")
    return extensao


def _extrair_registros(dados: object) -> list[dict]:
    """Localiza a lista de registros em um JSON, mesmo quando ela vem
    "envelopada" junto de metadados (ex: {"usuarios": [...], "total": 500})."""
    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        listas_de_registros = [
            valor
            for valor in dados.values()
            if isinstance(valor, list) and valor and all(isinstance(item, dict) for item in valor)
        ]
        if listas_de_registros:
            return max(listas_de_registros, key=len)
        return [dados]

    raise ValueError("Estrutura JSON não suportada: esperado uma lista de registros ou um objeto.")


def ler_arquivo(caminho: Path, formato: str) -> pd.DataFrame:
    try:
        if formato in ("csv", "txt"):
            return pd.read_csv(caminho, sep=None, engine="python")
        if formato in ("xlsx", "xls"):
            return pd.read_excel(caminho)
        if formato == "json":
            with open(caminho, encoding="utf-8") as arquivo_json:
                dados = json.load(arquivo_json)
            registros = _extrair_registros(dados)
            return pd.json_normalize(registros)
    except Exception as exc:
        raise ValueError(f"Não foi possível ler o arquivo como '{formato}': {exc}") from exc

    raise ValueError(f"Formato '{formato}' não suportado.")


def escrever_arquivo(df: pd.DataFrame, caminho: Path, formato: str) -> None:
    if formato in ("csv", "txt"):
        df.to_csv(caminho, index=False)
        return
    if formato in ("xlsx", "xls"):
        df.to_excel(caminho, index=False)
        return
    if formato == "json":
        df.to_json(caminho, orient="records", force_ascii=False, indent=2)
        return

    raise ValueError(f"Formato '{formato}' não suportado.")

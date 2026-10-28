import json
import uuid
from pathlib import Path
from typing import Protocol

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.arquivo_processado import ArquivoProcessado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.importacao.service import escrever_arquivo, ler_arquivo

PREVIEW_LINHAS = 10


class _VersaoGerada(Protocol):
    arquivo_id: object
    criado_em: object
    caminho_armazenado: str


def buscar_arquivo(arquivo_id: int, db: Session) -> ArquivoProcessado:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return arquivo


def carregar_dataframe(arquivo: ArquivoProcessado) -> pd.DataFrame:
    try:
        return ler_arquivo(Path(arquivo.caminho_armazenado), arquivo.formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def gerar_preview(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.head(PREVIEW_LINHAS).to_json(orient="records", date_format="iso"))


def salvar_dataframe(df: pd.DataFrame, diretorio: str, arquivo: ArquivoProcessado) -> Path:
    destino_dir = Path(diretorio)
    destino_dir.mkdir(parents=True, exist_ok=True)
    caminho = destino_dir / f"{uuid.uuid4()}_{arquivo.nome_arquivo}"
    escrever_arquivo(df, caminho, arquivo.formato)
    return caminho


def resolver_colunas_alvo(
    solicitadas: list[str] | None, classificacao: list[ColunaClassificada], df: pd.DataFrame
) -> list[str]:
    """Usa as colunas pedidas ou, se nenhuma foi informada, todas as sensíveis.
    Levanta 400 se alguma não existir no arquivo."""
    colunas = solicitadas if solicitadas is not None else [c.nome_coluna for c in classificacao if c.sensivel]

    invalidas = [c for c in colunas if c not in df.columns]
    if invalidas:
        raise HTTPException(status_code=400, detail=f"Colunas inexistentes no arquivo: {', '.join(invalidas)}")
    return colunas


def baixar_ultima_versao(
    db: Session, modelo: type[_VersaoGerada], arquivo: ArquivoProcessado, prefixo: str, msg_inexistente: str
) -> FileResponse:
    stmt = select(modelo).where(modelo.arquivo_id == arquivo.id).order_by(modelo.criado_em.desc())
    versao = db.scalars(stmt).first()
    if versao is None:
        raise HTTPException(status_code=404, detail=msg_inexistente)

    return FileResponse(versao.caminho_armazenado, filename=f"{prefixo}_{arquivo.nome_arquivo}")

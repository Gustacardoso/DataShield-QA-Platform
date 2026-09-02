import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_anonimizado import ArquivoAnonimizado
from app.models.arquivo_processado import ArquivoProcessado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.anonimizacao.schemas import AnonimizacaoResponse, AplicarAnonimizacaoRequest
from app.modules.anonimizacao.service import anonimizar_dataframe
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.service import escrever_arquivo, ler_arquivo

router = APIRouter(prefix="/api/anonimizacao", tags=["Anonimização"])


def _buscar_arquivo(arquivo_id: int, db: Session) -> ArquivoProcessado:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return arquivo


@router.post("/{arquivo_id}/aplicar", response_model=AnonimizacaoResponse)
def aplicar_anonimizacao(
    arquivo_id: int,
    payload: AplicarAnonimizacaoRequest = AplicarAnonimizacaoRequest(),
    db: Session = Depends(get_db),
) -> AnonimizacaoResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)
    classificacao = obter_ou_criar_classificacao(db, arquivo)

    colunas_alvo = (
        payload.colunas if payload.colunas is not None else [c.nome_coluna for c in classificacao if c.sensivel]
    )

    try:
        df = ler_arquivo(Path(arquivo.caminho_armazenado), arquivo.formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    colunas_invalidas = [c for c in colunas_alvo if c not in df.columns]
    if colunas_invalidas:
        raise HTTPException(
            status_code=400, detail=f"Colunas inexistentes no arquivo: {', '.join(colunas_invalidas)}"
        )

    df_anonimizado = anonimizar_dataframe(df, colunas_alvo)

    diretorio = Path(settings.anonymized_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    caminho_saida = diretorio / f"{uuid.uuid4()}_{arquivo.nome_arquivo}"
    escrever_arquivo(df_anonimizado, caminho_saida, arquivo.formato)

    db.add(
        ArquivoAnonimizado(
            arquivo_id=arquivo_id,
            caminho_armazenado=str(caminho_saida),
            colunas_anonimizadas=colunas_alvo,
        )
    )

    if colunas_alvo:
        db.execute(
            update(ColunaClassificada)
            .where(ColunaClassificada.arquivo_id == arquivo_id)
            .where(ColunaClassificada.nome_coluna.in_(colunas_alvo))
            .values(anonimizada=True)
        )

    db.commit()

    return AnonimizacaoResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        colunas_anonimizadas=colunas_alvo,
        preview=json.loads(df_anonimizado.head(10).to_json(orient="records", date_format="iso")),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_anonimizado(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    stmt = (
        select(ArquivoAnonimizado)
        .where(ArquivoAnonimizado.arquivo_id == arquivo_id)
        .order_by(ArquivoAnonimizado.criado_em.desc())
    )
    anonimizado = db.scalars(stmt).first()
    if anonimizado is None:
        raise HTTPException(status_code=404, detail="Este arquivo ainda não foi anonimizado")

    return FileResponse(anonimizado.caminho_armazenado, filename=f"anonimizado_{arquivo.nome_arquivo}")

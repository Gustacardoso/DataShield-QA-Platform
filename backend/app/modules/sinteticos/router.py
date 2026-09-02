import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_processado import ArquivoProcessado
from app.models.arquivo_sintetico import ArquivoSintetico
from app.modules.importacao.service import escrever_arquivo, ler_arquivo
from app.modules.sinteticos.schemas import GerarSinteticosRequest, SinteticosResponse
from app.modules.sinteticos.service import gerar_dataframe_sintetico

router = APIRouter(prefix="/api/sinteticos", tags=["Dados Sintéticos"])


def _buscar_arquivo(arquivo_id: int, db: Session) -> ArquivoProcessado:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return arquivo


@router.post("/{arquivo_id}/gerar", response_model=SinteticosResponse)
def gerar_sinteticos(
    arquivo_id: int,
    payload: GerarSinteticosRequest = GerarSinteticosRequest(),
    db: Session = Depends(get_db),
) -> SinteticosResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    try:
        df_original = ler_arquivo(Path(arquivo.caminho_armazenado), arquivo.formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    colunas = [str(coluna) for coluna in df_original.columns]
    dtypes = {coluna: df_original[coluna].dtype for coluna in colunas}

    df_sintetico = gerar_dataframe_sintetico(colunas, dtypes, payload.num_linhas)

    diretorio = Path(settings.synthetic_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    caminho_saida = diretorio / f"{uuid.uuid4()}_{arquivo.nome_arquivo}"
    escrever_arquivo(df_sintetico, caminho_saida, arquivo.formato)

    db.add(
        ArquivoSintetico(
            arquivo_id=arquivo_id,
            caminho_armazenado=str(caminho_saida),
            num_linhas=payload.num_linhas,
        )
    )
    db.commit()

    return SinteticosResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        num_linhas=payload.num_linhas,
        preview=json.loads(df_sintetico.head(10).to_json(orient="records", date_format="iso")),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_sintetico(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    stmt = (
        select(ArquivoSintetico)
        .where(ArquivoSintetico.arquivo_id == arquivo_id)
        .order_by(ArquivoSintetico.criado_em.desc())
    )
    sintetico = db.scalars(stmt).first()
    if sintetico is None:
        raise HTTPException(status_code=404, detail="Nenhum dado sintético foi gerado para este arquivo ainda")

    return FileResponse(sintetico.caminho_armazenado, filename=f"sintetico_{arquivo.nome_arquivo}")

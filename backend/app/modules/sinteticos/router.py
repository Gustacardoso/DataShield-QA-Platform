from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_sintetico import ArquivoSintetico
from app.modules.importacao.helpers import (
    baixar_ultima_versao,
    buscar_arquivo,
    carregar_dataframe,
    gerar_preview,
    salvar_dataframe,
)
from app.modules.sinteticos.schemas import GerarSinteticosRequest, SinteticosResponse
from app.modules.sinteticos.service import gerar_dataframe_sintetico

router = APIRouter(prefix="/api/sinteticos", tags=["Dados Sintéticos"])


@router.post("/{arquivo_id}/gerar", response_model=SinteticosResponse)
def gerar_sinteticos(
    arquivo_id: int,
    payload: GerarSinteticosRequest = GerarSinteticosRequest(),
    db: Session = Depends(get_db),
) -> SinteticosResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    df_original = carregar_dataframe(arquivo)

    colunas = [str(coluna) for coluna in df_original.columns]
    dtypes = {coluna: df_original[coluna].dtype for coluna in colunas}

    df_sintetico = gerar_dataframe_sintetico(colunas, dtypes, payload.num_linhas)
    caminho_saida = salvar_dataframe(df_sintetico, settings.synthetic_dir, arquivo)

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
        preview=gerar_preview(df_sintetico),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_sintetico(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    return baixar_ultima_versao(
        db, ArquivoSintetico, arquivo, "sintetico", "Nenhum dado sintético foi gerado para este arquivo ainda"
    )

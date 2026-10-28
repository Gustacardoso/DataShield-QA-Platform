from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_anonimizado import ArquivoAnonimizado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.anonimizacao.schemas import AnonimizacaoResponse, AplicarAnonimizacaoRequest
from app.modules.anonimizacao.service import anonimizar_dataframe
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.helpers import (
    baixar_ultima_versao,
    buscar_arquivo,
    carregar_dataframe,
    gerar_preview,
    resolver_colunas_alvo,
    salvar_dataframe,
)

router = APIRouter(prefix="/api/anonimizacao", tags=["Anonimização"])


@router.post("/{arquivo_id}/aplicar", response_model=AnonimizacaoResponse)
def aplicar_anonimizacao(
    arquivo_id: int,
    payload: AplicarAnonimizacaoRequest = AplicarAnonimizacaoRequest(),
    db: Session = Depends(get_db),
) -> AnonimizacaoResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    classificacao = obter_ou_criar_classificacao(db, arquivo)

    df = carregar_dataframe(arquivo)
    colunas_alvo = resolver_colunas_alvo(payload.colunas, classificacao, df)

    df_anonimizado = anonimizar_dataframe(df, colunas_alvo)
    caminho_saida = salvar_dataframe(df_anonimizado, settings.anonymized_dir, arquivo)

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
        preview=gerar_preview(df_anonimizado),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_anonimizado(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    return baixar_ultima_versao(
        db, ArquivoAnonimizado, arquivo, "anonimizado", "Este arquivo ainda não foi anonimizado"
    )

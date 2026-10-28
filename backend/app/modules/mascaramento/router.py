from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_mascarado import ArquivoMascarado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.helpers import (
    baixar_ultima_versao,
    buscar_arquivo,
    carregar_dataframe,
    gerar_preview,
    resolver_colunas_alvo,
    salvar_dataframe,
)
from app.modules.mascaramento.schemas import AplicarMascaramentoRequest, MascaramentoResponse
from app.modules.mascaramento.service import mascarar_dataframe

router = APIRouter(prefix="/api/mascaramento", tags=["Mascaramento"])


@router.post("/{arquivo_id}/aplicar", response_model=MascaramentoResponse)
def aplicar_mascaramento(
    arquivo_id: int,
    payload: AplicarMascaramentoRequest = AplicarMascaramentoRequest(),
    db: Session = Depends(get_db),
) -> MascaramentoResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    classificacao = obter_ou_criar_classificacao(db, arquivo)
    tipos_por_coluna = {c.nome_coluna: c.tipo_dado for c in classificacao}

    df = carregar_dataframe(arquivo)
    colunas_alvo = resolver_colunas_alvo(payload.colunas, classificacao, df)

    df_mascarado = mascarar_dataframe(df, colunas_alvo, tipos_por_coluna)
    caminho_saida = salvar_dataframe(df_mascarado, settings.masked_dir, arquivo)

    db.add(
        ArquivoMascarado(
            arquivo_id=arquivo_id,
            caminho_armazenado=str(caminho_saida),
            colunas_mascaradas=colunas_alvo,
        )
    )

    if colunas_alvo:
        db.execute(
            update(ColunaClassificada)
            .where(ColunaClassificada.arquivo_id == arquivo_id)
            .where(ColunaClassificada.nome_coluna.in_(colunas_alvo))
            .values(mascarada=True)
        )

    db.commit()

    return MascaramentoResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        colunas_mascaradas=colunas_alvo,
        preview=gerar_preview(df_mascarado),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_mascarado(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = buscar_arquivo(arquivo_id, db)
    return baixar_ultima_versao(db, ArquivoMascarado, arquivo, "mascarado", "Este arquivo ainda não foi mascarado")

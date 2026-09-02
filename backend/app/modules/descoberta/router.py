from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.arquivo_processado import ArquivoProcessado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.descoberta.schemas import ColunaClassificadaResponse, DescobertaResponse
from app.modules.descoberta.service import analisar_dataframe
from app.modules.importacao.service import ler_arquivo

router = APIRouter(prefix="/api/descoberta", tags=["Descoberta de Dados Sensíveis"])


def _buscar_arquivo(arquivo_id: int, db: Session) -> ArquivoProcessado:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return arquivo


@router.post("/{arquivo_id}/analisar", response_model=DescobertaResponse)
def analisar_arquivo(arquivo_id: int, db: Session = Depends(get_db)) -> DescobertaResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    try:
        df = ler_arquivo(Path(arquivo.caminho_armazenado), arquivo.formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    classificacoes = analisar_dataframe(df)

    db.execute(delete(ColunaClassificada).where(ColunaClassificada.arquivo_id == arquivo_id))
    registros = [
        ColunaClassificada(
            arquivo_id=arquivo_id,
            nome_coluna=c.nome_coluna,
            sensivel=c.sensivel,
            tipo_dado=c.tipo_dado,
        )
        for c in classificacoes
    ]
    db.add_all(registros)
    db.commit()

    return DescobertaResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        colunas=[ColunaClassificadaResponse.model_validate(c) for c in classificacoes],
        criado_em=datetime.now(UTC),
    )


@router.get("/{arquivo_id}", response_model=DescobertaResponse)
def obter_analise(arquivo_id: int, db: Session = Depends(get_db)) -> DescobertaResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    stmt = select(ColunaClassificada).where(ColunaClassificada.arquivo_id == arquivo_id)
    registros = list(db.scalars(stmt))
    if not registros:
        raise HTTPException(status_code=404, detail="Este arquivo ainda não foi analisado")

    return DescobertaResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        colunas=[ColunaClassificadaResponse.model_validate(r) for r in registros],
        criado_em=max(r.criado_em for r in registros),
    )

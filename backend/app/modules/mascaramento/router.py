import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.arquivo_mascarado import ArquivoMascarado
from app.models.arquivo_processado import ArquivoProcessado
from app.models.coluna_classificada import ColunaClassificada
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.service import escrever_arquivo, ler_arquivo
from app.modules.mascaramento.schemas import AplicarMascaramentoRequest, MascaramentoResponse
from app.modules.mascaramento.service import mascarar_dataframe

router = APIRouter(prefix="/api/mascaramento", tags=["Mascaramento"])


def _buscar_arquivo(arquivo_id: int, db: Session) -> ArquivoProcessado:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return arquivo


@router.post("/{arquivo_id}/aplicar", response_model=MascaramentoResponse)
def aplicar_mascaramento(
    arquivo_id: int,
    payload: AplicarMascaramentoRequest = AplicarMascaramentoRequest(),
    db: Session = Depends(get_db),
) -> MascaramentoResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)
    classificacao = obter_ou_criar_classificacao(db, arquivo)
    tipos_por_coluna = {c.nome_coluna: c.tipo_dado for c in classificacao}

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

    df_mascarado = mascarar_dataframe(df, colunas_alvo, tipos_por_coluna)

    diretorio = Path(settings.masked_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    caminho_saida = diretorio / f"{uuid.uuid4()}_{arquivo.nome_arquivo}"
    escrever_arquivo(df_mascarado, caminho_saida, arquivo.formato)

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
        preview=json.loads(df_mascarado.head(10).to_json(orient="records", date_format="iso")),
    )


@router.get("/{arquivo_id}/download")
def baixar_arquivo_mascarado(arquivo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    arquivo = _buscar_arquivo(arquivo_id, db)

    stmt = (
        select(ArquivoMascarado)
        .where(ArquivoMascarado.arquivo_id == arquivo_id)
        .order_by(ArquivoMascarado.criado_em.desc())
    )
    mascarado = db.scalars(stmt).first()
    if mascarado is None:
        raise HTTPException(status_code=404, detail="Este arquivo ainda não foi mascarado")

    return FileResponse(mascarado.caminho_armazenado, filename=f"mascarado_{arquivo.nome_arquivo}")

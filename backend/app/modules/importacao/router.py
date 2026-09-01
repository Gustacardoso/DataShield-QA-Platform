import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.storage import save_upload_file
from app.models.arquivo_processado import ArquivoProcessado
from app.modules.importacao.schemas import (
    ArquivoImportadoDetalhe,
    ArquivoImportadoResponse,
    ExcluirArquivosRequest,
)
from app.modules.importacao.service import formato_da_extensao, ler_arquivo

router = APIRouter(prefix="/api/importacao", tags=["Importação"])


@router.post("/upload", response_model=ArquivoImportadoResponse)
def upload_arquivo(arquivo: UploadFile, db: Session = Depends(get_db)) -> ArquivoImportadoResponse:
    try:
        formato = formato_da_extensao(arquivo.filename)
        caminho = save_upload_file(arquivo)
        df = ler_arquivo(caminho, formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    registro = ArquivoProcessado(
        nome_arquivo=arquivo.filename,
        formato=formato,
        caminho_armazenado=str(caminho),
        num_linhas=len(df),
        colunas=[str(coluna) for coluna in df.columns],
        preview=json.loads(df.head(10).to_json(orient="records", date_format="iso")),
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)

    return ArquivoImportadoResponse.model_validate(registro)


@router.get("/", response_model=list[ArquivoImportadoResponse])
def listar_arquivos(db: Session = Depends(get_db)) -> list[ArquivoProcessado]:
    stmt = select(ArquivoProcessado).order_by(ArquivoProcessado.criado_em.desc())
    return list(db.scalars(stmt))


@router.get("/{arquivo_id}", response_model=ArquivoImportadoDetalhe)
def obter_arquivo(arquivo_id: int, db: Session = Depends(get_db)) -> ArquivoProcessado:
    registro = db.get(ArquivoProcessado, arquivo_id)
    if registro is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return registro


@router.delete("/", status_code=204)
def excluir_arquivos(payload: ExcluirArquivosRequest, db: Session = Depends(get_db)) -> None:
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Nenhum id informado")

    stmt = select(ArquivoProcessado).where(ArquivoProcessado.id.in_(payload.ids))
    registros = db.scalars(stmt).all()

    for registro in registros:
        Path(registro.caminho_armazenado).unlink(missing_ok=True)
        db.delete(registro)

    db.commit()

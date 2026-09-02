from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.arquivo_processado import ArquivoProcessado
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.service import ler_arquivo
from app.modules.lgpd.schemas import AvaliacaoLgpdResponse, DadoEncontrado
from app.modules.lgpd.service import calcular_nivel_risco

router = APIRouter(prefix="/api/lgpd", tags=["Avaliação LGPD"])


@router.get("/{arquivo_id}", response_model=AvaliacaoLgpdResponse)
def avaliar_arquivo(arquivo_id: int, db: Session = Depends(get_db)) -> AvaliacaoLgpdResponse:
    arquivo = db.get(ArquivoProcessado, arquivo_id)
    if arquivo is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    classificacao = obter_ou_criar_classificacao(db, arquivo)
    sensiveis = [c for c in classificacao if c.sensivel]

    try:
        df = ler_arquivo(Path(arquivo.caminho_armazenado), arquivo.formato)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    dados_encontrados = [
        DadoEncontrado(
            coluna=coluna.nome_coluna,
            tipo_dado=coluna.tipo_dado,
            quantidade_encontrada=int(df[coluna.nome_coluna].notna().sum()) if coluna.nome_coluna in df.columns else 0,
            tratado=coluna.mascarada or coluna.anonimizada,
        )
        for coluna in sensiveis
    ]

    return AvaliacaoLgpdResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=arquivo.nome_arquivo,
        nivel_risco=calcular_nivel_risco(classificacao),
        total_colunas_sensiveis=len(sensiveis),
        colunas_tratadas=sum(1 for c in sensiveis if c.mascarada or c.anonimizada),
        dados_encontrados=dados_encontrados,
    )

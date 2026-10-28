from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.descoberta.service import obter_ou_criar_classificacao
from app.modules.importacao.helpers import buscar_arquivo, carregar_dataframe
from app.modules.lgpd.schemas import AvaliacaoLgpdResponse, DadoEncontrado
from app.modules.lgpd.service import calcular_nivel_risco

router = APIRouter(prefix="/api/lgpd", tags=["Avaliação LGPD"])


@router.get("/{arquivo_id}", response_model=AvaliacaoLgpdResponse)
def avaliar_arquivo(arquivo_id: int, db: Session = Depends(get_db)) -> AvaliacaoLgpdResponse:
    arquivo = buscar_arquivo(arquivo_id, db)

    classificacao = obter_ou_criar_classificacao(db, arquivo)
    sensiveis = [c for c in classificacao if c.sensivel]

    df = carregar_dataframe(arquivo)

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

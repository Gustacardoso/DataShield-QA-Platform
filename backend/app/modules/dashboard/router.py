from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.arquivo_processado import ArquivoProcessado
from app.models.arquivo_sintetico import ArquivoSintetico
from app.models.coluna_classificada import ColunaClassificada
from app.modules.dashboard.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    arquivos_processados = db.scalar(select(func.count()).select_from(ArquivoProcessado)) or 0
    dados_mascarados = (
        db.scalar(select(func.count()).select_from(ColunaClassificada).where(ColunaClassificada.mascarada.is_(True)))
        or 0
    )
    dados_anonimizados = (
        db.scalar(
            select(func.count()).select_from(ColunaClassificada).where(ColunaClassificada.anonimizada.is_(True))
        )
        or 0
    )
    dados_sinteticos_gerados = db.scalar(select(func.coalesce(func.sum(ArquivoSintetico.num_linhas), 0))) or 0

    total_sensiveis = (
        db.scalar(select(func.count()).select_from(ColunaClassificada).where(ColunaClassificada.sensivel.is_(True)))
        or 0
    )
    if total_sensiveis == 0:
        indice_conformidade_lgpd = 100.0
    else:
        tratadas_lgpd = (
            db.scalar(
                select(func.count())
                .select_from(ColunaClassificada)
                .where(ColunaClassificada.sensivel.is_(True))
                .where((ColunaClassificada.mascarada.is_(True)) | (ColunaClassificada.anonimizada.is_(True)))
            )
            or 0
        )
        indice_conformidade_lgpd = round(tratadas_lgpd / total_sensiveis * 100, 1)

    return DashboardSummary(
        arquivos_processados=arquivos_processados,
        dados_mascarados=dados_mascarados,
        dados_anonimizados=dados_anonimizados,
        dados_sinteticos_gerados=dados_sinteticos_gerados,
        indice_conformidade_lgpd=indice_conformidade_lgpd,
    )

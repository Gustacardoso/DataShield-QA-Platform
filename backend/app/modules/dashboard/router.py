from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.arquivo_processado import ArquivoProcessado
from app.modules.dashboard.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    arquivos_processados = db.scalar(select(func.count()).select_from(ArquivoProcessado)) or 0
    return DashboardSummary(
        arquivos_processados=arquivos_processados,
        dados_mascarados=0,
        dados_anonimizados=0,
        dados_sinteticos_gerados=0,
        indice_conformidade_lgpd=0.0,
    )

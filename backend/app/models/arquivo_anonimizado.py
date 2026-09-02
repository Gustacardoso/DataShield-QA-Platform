from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ArquivoAnonimizado(Base):
    __tablename__ = "arquivo_anonimizado"

    id: Mapped[int] = mapped_column(primary_key=True)
    arquivo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("arquivo_processado.id", ondelete="CASCADE"), index=True
    )
    caminho_armazenado: Mapped[str] = mapped_column(String(500))
    colunas_anonimizadas: Mapped[list[str]] = mapped_column(JSON)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

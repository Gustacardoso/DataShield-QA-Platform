from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ColunaClassificada(Base):
    __tablename__ = "coluna_classificada"

    id: Mapped[int] = mapped_column(primary_key=True)
    arquivo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("arquivo_processado.id", ondelete="CASCADE"), index=True
    )
    nome_coluna: Mapped[str] = mapped_column(String(255))
    sensivel: Mapped[bool] = mapped_column(Boolean)
    tipo_dado: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mascarada: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    anonimizada: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

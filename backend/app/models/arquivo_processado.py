from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ArquivoProcessado(Base):
    __tablename__ = "arquivo_processado"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    formato: Mapped[str] = mapped_column(String(20))
    caminho_armazenado: Mapped[str] = mapped_column(String(500))
    num_linhas: Mapped[int] = mapped_column(Integer)
    colunas: Mapped[list[str]] = mapped_column(JSON)
    preview: Mapped[list[dict]] = mapped_column(JSON)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

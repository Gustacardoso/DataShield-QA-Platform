from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ArquivoSintetico(Base):
    __tablename__ = "arquivo_sintetico"

    id: Mapped[int] = mapped_column(primary_key=True)
    arquivo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("arquivo_processado.id", ondelete="CASCADE"), index=True
    )
    caminho_armazenado: Mapped[str] = mapped_column(String(500))
    num_linhas: Mapped[int] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

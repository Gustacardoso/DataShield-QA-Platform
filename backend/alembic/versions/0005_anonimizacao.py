"""anonimizacao

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "coluna_classificada",
        sa.Column("anonimizada", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "arquivo_anonimizado",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "arquivo_id",
            sa.Integer(),
            sa.ForeignKey("arquivo_processado.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("caminho_armazenado", sa.String(length=500), nullable=False),
        sa.Column("colunas_anonimizadas", sa.JSON(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_arquivo_anonimizado_arquivo_id", "arquivo_anonimizado", ["arquivo_id"])


def downgrade() -> None:
    op.drop_index("ix_arquivo_anonimizado_arquivo_id", table_name="arquivo_anonimizado")
    op.drop_table("arquivo_anonimizado")
    op.drop_column("coluna_classificada", "anonimizada")

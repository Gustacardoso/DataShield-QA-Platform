"""mascaramento

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "coluna_classificada",
        sa.Column("mascarada", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "arquivo_mascarado",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "arquivo_id",
            sa.Integer(),
            sa.ForeignKey("arquivo_processado.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("caminho_armazenado", sa.String(length=500), nullable=False),
        sa.Column("colunas_mascaradas", sa.JSON(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_arquivo_mascarado_arquivo_id", "arquivo_mascarado", ["arquivo_id"])


def downgrade() -> None:
    op.drop_index("ix_arquivo_mascarado_arquivo_id", table_name="arquivo_mascarado")
    op.drop_table("arquivo_mascarado")
    op.drop_column("coluna_classificada", "mascarada")

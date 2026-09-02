"""coluna classificada

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coluna_classificada",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "arquivo_id",
            sa.Integer(),
            sa.ForeignKey("arquivo_processado.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome_coluna", sa.String(length=255), nullable=False),
        sa.Column("sensivel", sa.Boolean(), nullable=False),
        sa.Column("tipo_dado", sa.String(length=50), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_coluna_classificada_arquivo_id", "coluna_classificada", ["arquivo_id"])


def downgrade() -> None:
    op.drop_index("ix_coluna_classificada_arquivo_id", table_name="coluna_classificada")
    op.drop_table("coluna_classificada")

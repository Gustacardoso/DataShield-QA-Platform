"""sinteticos

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "arquivo_sintetico",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "arquivo_id",
            sa.Integer(),
            sa.ForeignKey("arquivo_processado.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("caminho_armazenado", sa.String(length=500), nullable=False),
        sa.Column("num_linhas", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_arquivo_sintetico_arquivo_id", "arquivo_sintetico", ["arquivo_id"])


def downgrade() -> None:
    op.drop_index("ix_arquivo_sintetico_arquivo_id", table_name="arquivo_sintetico")
    op.drop_table("arquivo_sintetico")

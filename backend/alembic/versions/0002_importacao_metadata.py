"""importacao metadata

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("arquivo_processado", sa.Column("formato", sa.String(length=20), nullable=False, server_default="csv"))
    op.add_column("arquivo_processado", sa.Column("caminho_armazenado", sa.String(length=500), nullable=False, server_default=""))
    op.add_column("arquivo_processado", sa.Column("num_linhas", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("arquivo_processado", sa.Column("colunas", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("arquivo_processado", sa.Column("preview", sa.JSON(), nullable=False, server_default="[]"))

    op.alter_column("arquivo_processado", "formato", server_default=None)
    op.alter_column("arquivo_processado", "caminho_armazenado", server_default=None)
    op.alter_column("arquivo_processado", "num_linhas", server_default=None)
    op.alter_column("arquivo_processado", "colunas", server_default=None)
    op.alter_column("arquivo_processado", "preview", server_default=None)


def downgrade() -> None:
    op.drop_column("arquivo_processado", "preview")
    op.drop_column("arquivo_processado", "colunas")
    op.drop_column("arquivo_processado", "num_linhas")
    op.drop_column("arquivo_processado", "caminho_armazenado")
    op.drop_column("arquivo_processado", "formato")

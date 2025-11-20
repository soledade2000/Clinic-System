"""add_new_cargos_enum

Revision ID: caf6de91df1f
Revises: d648bcd30f29
Create Date: 2025-09-19 14:13:59.441151

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'caf6de91df1f'
down_revision: Union[str, Sequence[str], None] = 'd648bcd30f29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: adiciona novos valores ao enum cargoenum."""
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'PSICOLOGO'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'SECRETARIA'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'PACIENTE'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'FISIOTERAPIA'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'MEDICO'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'NUTRICIONISTA'")
    op.execute("ALTER TYPE cargoenum ADD VALUE IF NOT EXISTS 'CLINICO'")


def downgrade() -> None:
    """Downgrade não implementado: remover valores de ENUM no Postgres é complexo."""
    pass

# alembic/env.py
import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# Adiciona app ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import *  # Importa todos os modelos automaticamente

# ---------------------
# ALEMBIC CONFIG
# ---------------------
config = context.config  # <<< Definido antes de usar

# Configura logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Usa variável de ambiente ou default local
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://clinic_admin:sua_senha_segura@db:5432/clinic_admin"
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# MetaData para autogenerate
target_metadata = Base.metadata

# ---------------------
# Funções de migração
# ---------------------
def run_migrations_offline() -> None:
    """Executa migrações no modo offline"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo online"""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Executa a migração dependendo do modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

from core.database import Base 
from core.database import engine as async_engine 
from core.database import AsyncSessionLocal 
from sqlalchemy.ext.asyncio import AsyncConnection 
from sqlalchemy import pool 
from sqlalchemy import text 

from logging.config import fileConfig
import asyncio # Necesario para asyncio.run()
from alembic import context

import core.models 
# ----------------------------------------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata # Ya apunta a tu Base.metadata, ¡correcto!

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    (Esta función no necesita cambios, ya es síncrona y no interactúa con DB real)
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Usaremos el motor asíncrono ya configurado en core.database
    connectable = async_engine

    async with connectable.connect() as connection:
        # Configuración específica para el dialecto SQLite
        if connection.dialect.name == 'sqlite':
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                render_as_batch=True, # Aquí va
            )
        else:
            # Configuración para otros dialectos (ej. PostgreSQL, que no necesita render_as_batch)
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

        await connection.run_sync( # `await` y `run_sync` para operaciones síncronas dentro de async
            do_run_migrations, # Pasamos la función auxiliar para ejecutar las migraciones
        )

def do_run_migrations(connection):
    """Auxiliary function to run migrations in a synchronous context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Estas opciones ya se manejan en run_migrations_online()
        # No ponemos render_as_batch=True aquí porque ya se configuró.
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Ejecutar la función asíncrona
    asyncio.run(run_migrations_online())


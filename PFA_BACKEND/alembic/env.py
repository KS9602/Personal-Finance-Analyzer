import asyncio
from logging.config import fileConfig
# from app.utils.lgging import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from app.core.config import settings

from app.models import Base
target_metadata = Base.metadata

# config
config = context.config
config.set_main_option("sqlalchemy.url",settings.DB_URL)
fileConfig(config.config_file_name)

DATABASE_URL = settings.DB_URL

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations())

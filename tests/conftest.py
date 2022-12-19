from asyncio import new_event_loop, set_event_loop, sleep
from logging import getLogger
from types import SimpleNamespace

import pytest
from aiogram import Bot
from alembic import command as alembic_command
from alembic.config import Config

from tests.fixtures import *  # noqa
from tests.utils import clear_database, make_alembic_config, postgres_dsn

from cinemabot.bot import get_bot_and_dispatcher
from cinemabot.config import get_settings
from cinemabot.database.connector import DatabaseConnector


logger = getLogger(__name__)
settings = get_settings()
# pytest_plugins = [
#     'fixtures',
# ]  # fixtures path here


@pytest.fixture(scope='session')
def event_loop():
    loop = new_event_loop()
    set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture(scope='session')
def alembic_config() -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cmd_options = SimpleNamespace(
        config="cinemabot/migrator/",
        name="alembic",
        pg_url=settings.database_url_for_sync_connection,
        raiseerr=False,
        x=None
    )
    return make_alembic_config(cmd_options)


@pytest.fixture(scope='session', autouse=True)
def migrate_postgres(alembic_config) -> None:
    alembic_command.upgrade(alembic_config, "head")


@pytest.fixture(scope='session')
async def engine():
    db = DatabaseConnector(dsn=settings.multihost_database_url, db_settings=settings.db_settings)
    await db.run()
    try:
        yield db
    finally:
        await db.stop()


@pytest.fixture(autouse=True)
async def truncate_tables(engine):
    yield
    await clear_database(engine)


@pytest.fixture
async def master_session(engine):
    """
    Should be used before engine fixture e.g.
    async def test_test(self, replica_session, engine, ...)
    or you get `failed: server closed the connection unexpectedly` error
    :param engine:
    :return:
    """
    async with engine.get_master_session() as session:
        yield session


@pytest.fixture
async def replica_session(engine):
    """
    Should be used before `engine` fixture e.g.
    async def test_test(self, replica_session, engine, ...)
    or you get `failed: server closed the connection unexpectedly` error
    :param engine:
    :return:
    """
    async with engine.get_replica_session() as session:
        yield session


@pytest.fixture(name='bot')
async def bot_fixture():
    """Bot fixture."""
    bot, _ = await get_bot_and_dispatcher()
    yield bot
    session = await bot.get_session()
    if session and not session.closed:
        await session.close()
        await sleep(0.2)

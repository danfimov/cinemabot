from collections import OrderedDict
from contextlib import asynccontextmanager
from re import compile

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from cinemabot.config import get_settings
from cinemabot.database.pool_manager.aiopg_sa import PoolManager


class Singleton(type):
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Singleton":  # type: ignore
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)  # noqa
        return cls._instance


class DatabaseConnector(metaclass=Singleton):
    DEFAULT_ACQUIRE_TIMEOUT: float = 1
    DEFAULT_REFRESH_DELAY: float = 1
    DEFAULT_REFRESH_TIMEOUT: float = 5
    DEFAULT_MASTER_AS_REPLICA_WEIGHT: float = 0.0
    DEFAULT_STOPWATCH_WINDOW_SIZE: int = 128
    SEARCH_HOST_REGEXP = compile(r"host=(.+?)\s")

    def __init__(self, dsn: str, db_settings: dict[str, str | int], statement_cache_size: int = 0):
        self._dsn = dsn
        self._db_settings = db_settings
        self._session_makers: OrderedDict[str, sessionmaker] = OrderedDict()
        self._statement_cache_size = statement_cache_size

    def _make_dsn_from_host(self, host: str) -> str:
        return (
            f'postgresql+asyncpg://{self._db_settings["user"]}:{self._db_settings["password"]}'
            f'@{host}:{self._db_settings["port"]}/{self._db_settings["database"]}?'
            f"prepared_statement_cache_size={self._statement_cache_size}"
        )

    async def run(self) -> None:
        self._create_session_makers()
        await self._set_engine()

    async def _set_engine(self) -> None:
        self._engine = PoolManager(
            dsn=self._dsn,
            acquire_timeout=self.DEFAULT_ACQUIRE_TIMEOUT,
            refresh_delay=self.DEFAULT_REFRESH_DELAY,
            refresh_timeout=self.DEFAULT_REFRESH_TIMEOUT,
            master_as_replica_weight=self.DEFAULT_MASTER_AS_REPLICA_WEIGHT,
            stopwatch_window_size=self.DEFAULT_STOPWATCH_WINDOW_SIZE,
        )

    def _create_session_makers(self) -> None:
        hosts: str = str(self._db_settings["host"])
        for host in hosts.split(","):
            async_engine = create_async_engine(
                self._make_dsn_from_host(host),
                echo=False,
                connect_args={
                    "ssl": self._db_settings["ssl_mode"],
                    "statement_cache_size": self._statement_cache_size,
                },
            )
            self._session_makers[host] = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def get_master_session(self) -> AsyncSession:
        async with self._engine.acquire_master() as master:
            master_host = self.SEARCH_HOST_REGEXP.search(master.connection.dsn).group(1)  # type: ignore
        master_pool = self._session_makers[master_host]
        async with master_pool.begin() as session:
            yield session

    @asynccontextmanager
    async def get_replica_session(self, fallback_master: bool = True) -> AsyncSession:
        async with self._engine.acquire_replica(fallback_master=fallback_master) as replica:
            replica_dsn = self.SEARCH_HOST_REGEXP.search(replica.connection.dsn).group(1)  # type: ignore
        replica_pool = self._session_makers[replica_dsn]
        async with replica_pool.begin() as session:
            yield session

    async def stop(self) -> None:
        await self._engine.close()


async def get_db() -> DatabaseConnector:
    settings = get_settings()
    db = DatabaseConnector(dsn=settings.multihost_database_url, db_settings=settings.db_settings)

    if getattr(db, "_engine", None) is None:
        await db.run()

    return db


__all__ = [
    "DatabaseConnector",
    "get_db",
]

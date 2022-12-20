import aiopg

from cinemabot.database.pool_manager.base import BasePoolManager
from cinemabot.database.pool_manager.utils import Dsn


class PoolManager(BasePoolManager):
    @staticmethod
    def get_pool_freesize(pool: aiopg.Pool) -> int:
        return pool.freesize

    @staticmethod
    def acquire_from_pool(pool, **kwargs):  # type: ignore
        return pool.acquire(**kwargs)

    @staticmethod
    async def release_to_pool(connection, pool, **kwargs):  # type: ignore
        return await pool.release(connection, **kwargs)

    async def _is_master(self, connection):  # type: ignore
        cursor = await connection.cursor()
        try:
            await cursor.execute("SHOW transaction_read_only")
            read_only = await cursor.fetchone()
            return read_only[0] == "off"
        finally:
            cursor.close()

    async def _pool_factory(self, dsn: Dsn) -> aiopg.Pool:
        return await aiopg.create_pool(str(dsn), **self.pool_factory_kwargs)

    @staticmethod
    def _prepare_pool_factory_kwargs(kwargs: dict) -> dict:  # type: ignore
        kwargs["minsize"] = kwargs.get("minsize", 1) + 1
        kwargs["maxsize"] = kwargs.get("maxsize", 10) + 1
        return kwargs

    @staticmethod
    async def _close(pool: aiopg.Pool) -> None:
        pool.close()
        await pool.wait_closed()

    @staticmethod
    def _terminate(pool: aiopg.Pool) -> None:
        pool.terminate()

    @staticmethod
    def is_connection_closed(connection: aiopg.Connection) -> bool:
        return connection.closed


__all__ = ["PoolManager"]

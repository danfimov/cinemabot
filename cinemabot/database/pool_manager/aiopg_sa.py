import aiopg.sa

from cinemabot.database.pool_manager.aiopg import PoolManager as AioPgPoolManager
from cinemabot.database.pool_manager.utils import Dsn


class PoolManager(AioPgPoolManager):
    async def _is_master(self, connection: aiopg.sa.connection.SAConnection) -> bool:
        read_only = await connection.scalar("SHOW transaction_read_only")
        return read_only == "off"

    async def _pool_factory(self, dsn: Dsn) -> aiopg.pool.Pool:
        return await aiopg.sa.create_engine(
            str(dsn),
            **self.pool_factory_kwargs,
        )


__all__ = ["PoolManager"]

import random
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from cinemabot.database.pool_manager.base import BasePoolManager


class BaseBalancerPolicy:
    def __init__(self, pool_manager: "BasePoolManager") -> None:
        self._pool_manager = pool_manager

    async def get_pool(self, read_only: bool, fallback_master: Optional[bool] = None, master_as_replica_weight: Optional[float] = None) -> None:
        if not read_only and master_as_replica_weight is not None:
            raise ValueError(
                "Field master_as_replica_weight is used only when " "read_only is True",
            )

        choose_master_as_replica = False
        if master_as_replica_weight is not None:
            rand = random.random()
            choose_master_as_replica = 0 < rand <= master_as_replica_weight

        return await self._get_pool(
            read_only=read_only,
            fallback_master=fallback_master or choose_master_as_replica,
            choose_master_as_replica=choose_master_as_replica,
        )

    @abstractmethod
    async def _get_pool(self, read_only: bool, fallback_master: Optional[bool] = None, choose_master_as_replica: bool = False) -> None:
        pass


__all__ = ["BaseBalancerPolicy"]

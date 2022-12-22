from random import randint

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.core import get_search_history
from cinemabot.database.models import SearchHistory, User


class TestSearchHistory:
    @staticmethod
    async def create_search_history(session: AsyncSession, user_id: int, request_number: int = 10) -> None:
        for request_index in range(1, request_number + 1):
            create_query = (
                insert(SearchHistory)
                .values(user_id=user_id, request_text=f'request #{request_index}')
            )
            await session.execute(create_query)

    async def test_empty_history(self, replica_session: AsyncSession) -> None:
        user_id = randint(1, 1000)
        assert await get_search_history(replica_session, user_id, 1) == []

    async def test_first_page(self, replica_session: AsyncSession, user: User) -> None:
        await self.create_search_history(replica_session, user.id, 10)

        first_page_data = await get_search_history(replica_session, user.id, 1)
        assert len(first_page_data) == 10
        assert isinstance(first_page_data, list)
        assert isinstance(first_page_data[0], SearchHistory)
        assert await get_search_history(replica_session, user.id, 2) == []

    async def test_not_full_page(self, replica_session: AsyncSession, user: User) -> None:
        await self.create_search_history(replica_session, user.id, 16)
        first_page_data = await get_search_history(replica_session, user.id, 2)
        assert len(first_page_data) == 6

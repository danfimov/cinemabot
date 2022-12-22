from random import randint

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.core import get_or_create_user
from cinemabot.database.models import User


class TestUserFunctions:
    @staticmethod
    async def check_user_exist(session: AsyncSession, user_id: int) -> bool:
        user_exist_query = select(User).filter(User.id == user_id)
        user_from_base = (await session.execute(user_exist_query)).fetchone()
        return user_from_base is not None

    async def test_create_user(self, master_session: AsyncSession) -> None:
        new_user_id = randint(1, 1000)
        assert await self.check_user_exist(master_session, new_user_id) is False
        user_from_function = await get_or_create_user(master_session, new_user_id)
        assert isinstance(user_from_function, User)
        assert await self.check_user_exist(master_session, new_user_id) is True

    async def test_existing_user(self, master_session: AsyncSession, user: User) -> None:
        user_from_function = await get_or_create_user(
            master_session,
            user.id
        )
        assert isinstance(user_from_function, User)
        assert user_from_function.id == user.id

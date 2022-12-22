from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.core import increase_number_of_film_view
from cinemabot.database.models import Film, UserFilmView


class TestUserFilmViewFunctions:
    @staticmethod
    async def get_number_of_views(session: AsyncSession, user_film_view_id: UUID4) -> int:
        query = select(UserFilmView.views).filter(UserFilmView.id == user_film_view_id)
        return await session.scalar(query)

    async def test_user_film_view_increase_views(
        self,
        user_film_view: UserFilmView,
        film: Film,
        master_session: AsyncSession,
    ) -> None:
        assert await self.get_number_of_views(master_session, user_film_view.id) == 0
        await increase_number_of_film_view(
            master_session,
            user_film_view.user_id,
            film.kinopoisk_id,
            film.name_ru,
            film.name_eng,
        )
        assert await self.get_number_of_views(master_session, user_film_view.id) == 1

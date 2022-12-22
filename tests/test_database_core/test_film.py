from random import randint
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.core import get_or_create_film
from cinemabot.database.models import Film


class TestFilmFunctions:
    @staticmethod
    async def check_film_exist(session: AsyncSession, film_kinopoisk_id: int) -> bool:
        film_exist_query = select(Film).filter(Film.kinopoisk_id == film_kinopoisk_id)
        film_from_base = (await session.execute(film_exist_query)).fetchone()
        return film_from_base is not None

    async def test_create_film(self, master_session: AsyncSession) -> None:
        new_film_kinopoisk_id = randint(1, 1000)
        name_ru, name_eng = str(uuid4()), str(uuid4())
        assert await self.check_film_exist(master_session, new_film_kinopoisk_id) is False
        film_from_function = await get_or_create_film(
            master_session,
            new_film_kinopoisk_id,
            name_ru,
            name_eng
        )
        assert isinstance(film_from_function, Film)
        assert await self.check_film_exist(master_session, new_film_kinopoisk_id)

    async def test_existing_film(self, master_session: AsyncSession, film: Film) -> None:
        film_from_function = await get_or_create_film(
            master_session,
            film.kinopoisk_id,
            film.name_ru,
            film.name_eng,
        )
        assert isinstance(film_from_function, Film)
        assert film_from_function.id == film.id

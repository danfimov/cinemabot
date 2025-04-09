import sqlalchemy as sa

from cinemabot.domain.repository.storage import AbstractStorageRepository
from cinemabot.infrastructure.database import session_provider
from cinemabot.infrastructure.database.schemas import Film, SearchHistory, User, UserFilmView


class StorageRepository(AbstractStorageRepository):
    def __init__(self, session_provider: session_provider.AsyncPostgresSessionProvider) -> None:
        self._session_provider = session_provider

    async def create_user(
        self,
        user_id: int,
        get_or_create: bool = False,
    ) -> User:
        async with self._session_provider.session() as session:
            if get_or_create:
                existing_user_query = sa.select(User).filter(User.id == user_id)
                existing_user = await session.scalar(existing_user_query)
                if existing_user is not None:
                    return existing_user
            create_user_query = sa.insert(User).values(id=user_id).returning(User)
            await session.execute(create_user_query)
            return await session.scalar(existing_user_query)

    async def get_or_create_film(
        self,
        film_kinopoisk_id: int,
        film_name_ru: str | None,
        film_name_eng: str | None,
    ) -> Film:
        if not film_name_ru:
            film_name_ru = ""
        if not film_name_eng:
            film_name_eng = ""

        async with self._session_provider.session() as session:
            existing_film_query = sa.select(Film).filter(Film.kinopoisk_id == film_kinopoisk_id)
            existing_film = await session.scalar(existing_film_query)
            if existing_film is not None:
                return existing_film

            create_film_query = sa.insert(Film).values(
                kinopoisk_id=film_kinopoisk_id,
                name_ru=film_name_ru,
                name_eng=film_name_eng,
            )
            await session.execute(create_film_query)
            return await session.scalar(existing_film_query)

    async def get_or_create_user_film_view(
        self,
        user_id: int,
        film_id: int,
    ) -> UserFilmView:
        async with self._session_provider.session() as session:
            existing_user_film_view_query = sa.select(UserFilmView).filter(
                UserFilmView.film_id == film_id, UserFilmView.user_id == user_id
            )
            existing_film = await session.scalar(existing_user_film_view_query)
            if existing_film is not None:
                return existing_film

            create_user_film_view_query = sa.insert(UserFilmView).values(
                film_id=film_id,
                user_id=user_id,
            )
            await session.execute(create_user_film_view_query)
            return await session.scalar(existing_user_film_view_query)

    async def add_request_to_history(
        self,
        user_id: int,
        request_text: str,
    ) -> None:
        async with self._session_provider.session() as session:
            user = await self.create_user(user_id, get_or_create=True)
            query = sa.insert(SearchHistory).values(user_id=user.id, request_text=request_text)
            await session.execute(query)

    async def increase_number_of_film_view(
        self,
        user_id: int,
        film_kinopoisk_id: int,
        film_name_ru: str,
        film_name_eng: str,
    ) -> None:
        async with self._session_provider.session() as session:
            film = await self.get_or_create_film(film_kinopoisk_id, film_name_ru, film_name_eng)
            user = await self.create_user(user_id, get_or_create=True)
            user_film_view = await self.get_or_create_user_film_view(user.id, film.id)

            query = (
                sa.update(UserFilmView)
                .filter(UserFilmView.id == user_film_view.id)
                .values(views=user_film_view.views + 1)
            )
            await session.execute(query)

    async def get_search_history(
        self,
        user_id: int,
        page_number: int,
        page_size: int = 10,
    ) -> list[SearchHistory]:
        async with self._session_provider.session() as session:
            query = (
                sa.select(SearchHistory)
                .filter(SearchHistory.user_id == user_id)
                .limit(page_size)
                .offset((page_number - 1) * 10)
                .order_by(SearchHistory.created_at.desc())
            )
            history_rows = (await session.execute(query)).fetchall()
            return [row[0] for row in history_rows]

    async def get_stats(
        self,
        user_id: int,
        page_number: int,
        page_size: int = 10,
    ) -> list[tuple[int, str]]:
        async with self._session_provider.session() as session:
            query = (
                sa.select(UserFilmView.views, Film.name_ru)
                .join(
                    Film,
                    Film.id == UserFilmView.film_id,
                )
                .filter(UserFilmView.user_id == user_id)
                .order_by(UserFilmView.views.desc())
                .limit(page_size)
                .offset((page_number - 1) * 10)
            )
            stat_rows = (await session.execute(query)).fetchall()
            return [(row[0], row[1]) for row in stat_rows]

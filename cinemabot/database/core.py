from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.models import Film, SearchHistory, User, UserFilmView


async def create_user(
    session: AsyncSession,
    user_id: int,
) -> None:
    create_user_query = insert(User).values(id=user_id).returning(User)
    await session.execute(create_user_query)


async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
) -> User:
    existing_user_query = select(User).filter(User.id == user_id)
    existing_user = await session.scalar(existing_user_query)
    if existing_user is not None:
        return existing_user
    await create_user(session, user_id)
    return await session.scalar(existing_user_query)


async def get_or_create_film(
    session: AsyncSession,
    film_kinopoisk_id: int,
    film_name_ru: str,
    film_name_eng: str,
) -> Film:
    existing_film_query = select(Film).filter(Film.kinopoisk_id == film_kinopoisk_id)
    existing_film = await session.scalar(existing_film_query)
    if existing_film is not None:
        return existing_film

    create_film_query = insert(Film).values(
        kinopoisk_id=film_kinopoisk_id,
        name_ru=film_name_ru,
        name_eng=film_name_eng,
    )
    await session.execute(create_film_query)
    return await session.scalar(existing_film_query)


async def get_or_create_user_film_view(
    session: AsyncSession,
    user_id: int,
    film_id: int,
) -> UserFilmView:
    existing_user_film_view_query = select(UserFilmView).filter(UserFilmView.film_id == film_id, UserFilmView.user_id == user_id)
    existing_film = await session.scalar(existing_user_film_view_query)
    if existing_film is not None:
        return existing_film

    create_user_film_view_query = insert(UserFilmView).values(
        film_id=film_id,
        user_id=user_id,
    )
    await session.execute(create_user_film_view_query)
    return await session.scalar(existing_user_film_view_query)


async def add_request_to_history(
    session: AsyncSession,
    user_id: int,
    request_text: str,
) -> None:
    user = await get_or_create_user(session, user_id)
    query = insert(SearchHistory).values(user_id=user.id, request_text=request_text)
    await session.execute(query)


async def increase_number_of_film_view(
    session: AsyncSession,
    user_id: int,
    film_kinopoisk_id: int,
    film_name_ru: str,
    film_name_eng: str,
) -> None:
    film = await get_or_create_film(session, film_kinopoisk_id, film_name_ru, film_name_eng)
    user = await get_or_create_user(session, user_id)
    user_film_view = await get_or_create_user_film_view(session, user.id, film.id)

    query = update(UserFilmView).filter(UserFilmView.id == user_film_view.id).values(views=user_film_view.views + 1)
    await session.execute(query)


async def get_search_history(
    session: AsyncSession,
    user_id: int,
    page_number: int,
    page_size: int = 10,
) -> list[SearchHistory]:
    query = select(SearchHistory).filter(SearchHistory.user_id == user_id).limit(page_size).offset((page_number - 1) * 10).order_by(SearchHistory.dt_created.desc())
    history_rows = (await session.execute(query)).fetchall()
    return [row[0] for row in history_rows]


async def get_stats(
    session: AsyncSession,
    user_id: int,
    page_number: int,
    page_size: int = 10,
) -> list[tuple[int, str]]:
    query = (
        select(UserFilmView.views, Film.name_ru)
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

from pytest import fixture
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.models import Film, User, UserFilmView


@fixture
async def user_film_view(master_session: AsyncSession, user: User, film: Film) -> UserFilmView:
    create_query = (
        insert(UserFilmView)
        .values(
            user_id=user.id,
            film_id=film.id,
        )
    )
    await master_session.execute(create_query)
    return await master_session.scalar(
        select(UserFilmView)
        .filter(
            UserFilmView.film_id == film.id,
            UserFilmView.user_id == user.id,
        )
    )

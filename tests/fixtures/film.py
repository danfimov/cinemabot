from random import randint
from uuid import uuid4

from pytest import fixture
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from cinemabot.database.models import Film


@fixture
async def film(master_session: AsyncSession) -> Film:
    kinopoisk_id = randint(1, 1000)
    create_query = (
        insert(Film)
        .values(
            name_ru=str(uuid4()),
            name_eng=str(uuid4()),
            kinopoisk_id=kinopoisk_id,
        )
    )
    await master_session.execute(create_query)
    return await master_session.scalar(select(Film).filter(Film.kinopoisk_id == kinopoisk_id))

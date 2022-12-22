from random import randint

from pytest import fixture
from sqlalchemy import insert, select

from cinemabot.database.connector import DatabaseConnector
from cinemabot.database.models import User


@fixture
async def user(engine: DatabaseConnector) -> User:
    async with engine.get_master_session() as session:
        user_id = randint(1, 1000)
        create_user_query = insert(User).values(id=user_id).returning(User)
        await session.execute(create_user_query)
        user_query = select(User).filter(User.id == user_id)
        return await session.scalar(user_query)

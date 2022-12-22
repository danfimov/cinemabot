from aiogram import Bot
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import FakeTelegram

from cinemabot.database.models import User
from cinemabot.handlers.start import start_command_executor


USER = {
    "id": 12345678,
    "is_bot": False,
    "first_name": "FirstName",
    "last_name": "LastName",
    "username": "username",
    "language_code": "ru",
}

CHAT = {
    "id": 12345678,
    "first_name": "FirstName",
    "last_name": "LastName",
    "username": "username",
    "type": "private",
}

MESSAGE = {
    "message_id": 11223,
    "from": USER,
    "chat": CHAT,
    "date": 1508709711,
    "text": "/start",
}


class TestBotHandlers:
    @staticmethod
    async def check_user_exist(session: AsyncSession, user_id: int) -> bool:
        user_exist_query = select(User).filter(User.id == user_id)
        user_from_base = (await session.execute(user_exist_query)).fetchone()
        return user_from_base is not None

    async def test_start(self, master_session: AsyncSession, bot: Bot) -> None:
        message = Message(**MESSAGE)
        Bot.set_current(bot)
        assert await self.check_user_exist(master_session, message.from_user.id) is False
        async with FakeTelegram(message_data=message):
            await start_command_executor(message)
        assert await self.check_user_exist(master_session, message.from_user.id)

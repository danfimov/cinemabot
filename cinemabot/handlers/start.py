from aiogram.types import Message

from cinemabot.database.connector import get_db
from cinemabot.database.core import get_or_create_user


async def start_command_executor(message: Message) -> None:
    db = await get_db()
    async with db.get_master_session() as session:
        await get_or_create_user(session, message.from_user.id)
    await message.answer(
        "Добро пожаловать! Чтобы быстро найти фильм воспользуйся командой `/find название_фильма`.\n\n" "Информацию об остальных командах можно получить с помощью команды `/help`",
        parse_mode="markdown",
    )

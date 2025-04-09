import aiogram
from aiogram import filters, types

from cinemabot import dependencies


router = aiogram.Router()


@router.message(filters.Command("start"))
async def start_command_executor(message: types.Message) -> None:
    storage = dependencies.get_storage_repository()
    user = message.from_user
    if not user:
        await message.answer("Извините, но я не могу определить пользователя по этому сообщению.")
        return
    await storage.create_user(user.id, get_or_create=True)
    await message.answer(
        "Добро пожаловать! Чтобы быстро найти фильм воспользуйся командой `/find название_фильма`.\n\n"
        "Информацию об остальных командах можно получить с помощью команды `/help`",
        parse_mode="markdown",
    )

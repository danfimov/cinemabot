from aiogram.types import Message


async def help_command_executor(message: Message) -> None:
    command_help = {
        "/start": "   Начать работу с ботом. Не делает ничего, зато +1 команда",
        "/find": "      Найти фильм по названию. "
        "Вам будут предлагаться фильмы из поиска (по одному за раз). "
        "Если фильм найден, вы сможете посмотреть подробную информацию, а также получить ссылку на Кинопоиск",
        "/history": "Посмотреть историю поиска. " "Вы увидите список вида `(дата_поиска) название_фильма`, упорядоченный по убыванию даты поиска",
        "/stats": "    Посмотреть статистику показа фильмов. " "Вы увидите список, состоящий из элементов `(количество_показов_вам) название_фильма`. " "Он упорядочен по убыванию количества показов",
        "/help": "      Посмотреть список команд с их описанием. *(Вы здесь)*",
    }

    command_help_text = ";\n\n".join(map(lambda x: f"`{x[0]}`: {x[1]}", command_help.items()))

    await message.answer(
        f"Список команд:\n\n {command_help_text}",
        parse_mode="markdown",
    )


async def need_help_command_executor(message: Message) -> None:
    await message.answer(
        f"Не знаю, что такое: {message.text}.\n\n" f"Список доступных действий доступен по команде `/help`",
        parse_mode="markdown",
    )

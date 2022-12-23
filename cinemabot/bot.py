from logging import INFO, basicConfig, getLogger

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import BotCommand
from cashews import cache

from cinemabot.config import get_settings
from cinemabot.handlers import (
    action_in_canceled_find,
    cancel_find,
    find_command_executor,
    help_command_executor,
    history_command_executor,
    history_next_page,
    history_prev_page,
    movie_description_in_find,
    need_help_command_executor,
    next_movie_in_find,
    start_command_executor,
    stats_command_executor,
    stats_next_page,
    stats_prev_page,
)
from cinemabot.state import UserState


logger = getLogger(__name__)


# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Посмотреть список команд"),
        BotCommand(command="/find", description="Найти фильм по названию"),
        BotCommand(command="/history", description="Посмотреть историю поиска"),
        BotCommand(command="/stats", description="Посмотреть статистику показа фильмов"),
    ]
    await bot.set_my_commands(commands)


def register_handlers_common(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command_executor, commands=["start"], state="*")
    dp.register_message_handler(help_command_executor, commands=["help"], state="*")
    dp.register_message_handler(find_command_executor, commands=["find"], state="*")
    dp.register_message_handler(history_command_executor, commands=["history"], state="*")
    dp.register_message_handler(stats_command_executor, commands=["stats"], state="*")
    dp.register_message_handler(need_help_command_executor, state="*")
    dp.register_callback_query_handler(
        next_movie_in_find,
        lambda c: c.data == "find_command_next_button",
        state=UserState.find_state,
    )
    dp.register_callback_query_handler(
        movie_description_in_find,
        lambda c: c.data == "find_command_detail_button",
        state=UserState.find_state,
    )
    dp.register_callback_query_handler(
        cancel_find,
        lambda c: c.data == "find_command_stop_button",
        state=UserState.find_state,
    )
    dp.register_callback_query_handler(
        action_in_canceled_find,
        lambda c: c.data == "find_command_stop_button" or c.data == "find_command_detail_button" or c.data == "find_command_next_button",
        state="*",
    )
    dp.register_callback_query_handler(
        history_next_page,
        lambda c: c.data == "history_command_next_button",
        state=UserState.history_state,
    )
    dp.register_callback_query_handler(
        history_prev_page,
        lambda c: c.data == "history_command_prev_button",
        state=UserState.history_state,
    )
    dp.register_callback_query_handler(
        stats_next_page,
        lambda c: c.data == "stats_command_next_button",
        state=UserState.stats_state,
    )
    dp.register_callback_query_handler(
        stats_prev_page,
        lambda c: c.data == "stats_command_prev_button",
        state=UserState.stats_state,
    )


async def get_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    # Настройка логирования в stdout
    basicConfig(
        level=INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    cache.setup("redis://0.0.0.0/", db=1, wait_for_connection_timeout=0.5, safe=False, hash_key=b"cinemabot", enable=True)

    bot = Bot(token=get_settings().BOT_TOKEN)
    dispatcher = Dispatcher(bot, storage=RedisStorage2())

    # Включение мидлвали для логирования команд
    dispatcher.middleware.setup(LoggingMiddleware())

    # Регистрация хэндлеров
    register_handlers_common(dispatcher)

    # Установка команд бота
    await set_commands(bot)
    return bot, dispatcher


__all__ = [
    "get_bot_and_dispatcher",
]

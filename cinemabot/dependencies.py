import aiogram
from aiogram.types import BotCommand

from cinemabot import handlers
from cinemabot.domain.repository.storage import AbstractStorageRepository
from cinemabot.infrastructure import settings
from cinemabot.infrastructure.clients import kinopoisk
from cinemabot.infrastructure.database import session_provider
from cinemabot.infrastructure.repository.storage import StorageRepository


_settings: settings.Settings | None = None
_dispatcher: aiogram.Dispatcher | None = None
_bot: aiogram.Bot | None = None
_session_provider: session_provider.AsyncPostgresSessionProvider | None = None
_storage_repository: AbstractStorageRepository | None = None
_kinopoisk_client: kinopoisk.KinopoiskClient | None = None  # TODO: правильнее будет определить абстрактный data source


def get_settings() -> settings.Settings:
    global _settings
    if _settings is None:
        _settings = settings.Settings()
    return _settings


async def get_dispatcher_and_bot() -> tuple[aiogram.Dispatcher, aiogram.Bot]:
    global _dispatcher, _bot
    if not _dispatcher or not _bot:
        settings = get_settings()
        _bot = aiogram.Bot(token=settings.bot.token)
        _dispatcher = aiogram.Dispatcher()  # TODO: add storage storage=RedisStorage2(host="cinemabot_redis")

        _dispatcher.include_router(handlers.start_router)
        _dispatcher.include_router(handlers.find_router)
        _dispatcher.include_router(handlers.stats_router)
        _dispatcher.include_router(handlers.history_router)
        _dispatcher.include_router(handlers.help_router)

        # Установка команд бота
        commands = [
            BotCommand(command="/start", description="Начать работу с ботом"),
            BotCommand(command="/help", description="Посмотреть список команд"),
            BotCommand(command="/find", description="Найти фильм по названию"),
            BotCommand(command="/history", description="Посмотреть историю поиска"),
            BotCommand(command="/stats", description="Посмотреть статистику показа фильмов"),
        ]
        await _bot.set_my_commands(commands)
    return _dispatcher, _bot


def get_session_provider() -> session_provider.AsyncPostgresSessionProvider:
    global _session_provider
    if _session_provider is None:
        settings = get_settings()
        _session_provider = session_provider.AsyncPostgresSessionProvider(
            connection_settings=settings.postgres,
        )
    return _session_provider


def get_storage_repository() -> AbstractStorageRepository:
    global _storage_repository
    if _storage_repository is None:
        _storage_repository = StorageRepository(
            session_provider=get_session_provider(),
        )
    return _storage_repository


def get_kinopoisk_client() -> kinopoisk.KinopoiskClient:
    global _kinopoisk_client
    if _kinopoisk_client is None:
        settings = get_settings()
        _kinopoisk_client = kinopoisk.KinopoiskClient(
            base_url=settings.kinopoisk.base_url,
            api_key=settings.kinopoisk.api_key,
        )
    return _kinopoisk_client

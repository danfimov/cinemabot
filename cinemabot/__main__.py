import uvloop

from cinemabot import dependencies
from cinemabot.infrastructure.logs import configure_logging


async def main() -> None:
    settings = dependencies.get_settings()
    configure_logging(
        path_to_log_config=settings.log_config_path,
        root_level=settings.log_level,
    )
    dispatcher, bot = await dependencies.get_dispatcher_and_bot()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    uvloop.run(main())

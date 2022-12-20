from asyncio import run

from cinemabot.bot import get_bot_and_dispatcher


async def main() -> None:
    bot, dispatcher = await get_bot_and_dispatcher()

    await dispatcher.start_polling()


if __name__ == "__main__":
    run(main())

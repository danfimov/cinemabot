from os import environ

from pydantic import BaseSettings


class BotMixin(BaseSettings):
    BOT_TOKEN: str = environ.get("BOT_TOKEN", "")

    # WEBHOOK_HOST: str = environ.get("WEBHOOK_HOST", "https://cloud.yandex.ru")
    # WEBHOOK_PATH: str = environ.get("WEBHOOK_PATH", f'/webhook/{BOT_TOKEN}')
    # WEBHOOK_URL: str = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
    #
    # WEBAPP_HOST = '0.0.0.0'
    # WEBAPP_PORT: int = int(environ.get('PORT', default="8000"))

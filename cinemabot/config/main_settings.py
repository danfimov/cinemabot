from .bot_mixin import BotMixin
from .kinopoisk_mixin import KinopoiskMixin
from .postgres_mixin import PostgresMixin


class MainSettings(KinopoiskMixin, BotMixin, PostgresMixin):
    ...


def get_settings() -> MainSettings:
    return MainSettings()


__all__ = [
    "get_settings",
]

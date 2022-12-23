from os import environ

from pydantic import BaseSettings


class KinopoiskMixin(BaseSettings):
    KINOPOISK_API_KEY: str = environ.get("KINOPOISK_API_KEY", "")  # https://kinopoiskapiunofficial.tech/documentation/api/

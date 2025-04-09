import os
import pathlib
import typing as tp
import urllib.parse

import pydantic
import pydantic_settings


def _remove_prefix(value: str, prefix: str) -> str:
    if value.startswith(prefix):
        return value[len(prefix) :]
    return value


class PostgresSettings(pydantic.BaseModel):
    """Настройки для подключения к PostgreSQL."""

    driver: str = "postgresql+asyncpg"
    host: str
    port: int = 5432
    user: str
    password: pydantic.SecretStr
    database: str

    min_pool_size: int
    max_pool_size: int

    @property
    def dsn(self) -> pydantic.SecretStr:
        """
        Возвращает строку подключения к PostgreSQL составленную из параметров класса.

        Пример использования с asyncpg:

            >>> import asyncpg
            >>> async def create_pool(settings: PostgresSettings) -> asyncpg.pool.Pool:
            >>>     return await asyncpg.create_pool(
            >>>            dsn=settings.postgres.dsn.get_secret_value(),
            >>>            min_size=settings.postgres.min_size,
            >>>            max_size=settings.postgres.max_size,
            >>>            statement_cache_size=settings.postgres.statement_cache_size,
            >>>     )

        Пример использования с SQLAlchemy:

            >>> import sqlalchemy
            >>> async def create_pool(settings: PostgresSettings) -> sqlalchemy.ext.asyncio.AsyncEngine:
            >>>     return sqlalchemy.ext.asyncio.create_async_engine(
            >>>         settings.postgres.dsn.get_secret_value()
            >>>     )
        """
        return pydantic.SecretStr(
            f"{self.driver}://{self.user}:{urllib.parse.quote(self.password.get_secret_value())}@{self.host}:{self.port}/{self.database}",
        )

    @pydantic.model_validator(mode="before")
    @classmethod
    def __parse_dsn(cls, values: dict[str, tp.Any]) -> dict[str, tp.Any]:
        dsn = values.get("dsn")
        if dsn is not None and not isinstance(dsn, str):
            msg = "Field 'dsn' must be str"
            raise TypeError(msg)
        if not dsn:
            return values
        parsed_dsn = urllib.parse.urlparse(dsn)
        values["driver"] = parsed_dsn.scheme
        values["host"] = parsed_dsn.hostname
        values["port"] = parsed_dsn.port
        values["user"] = parsed_dsn.username
        values["password"] = parsed_dsn.password
        values["database"] = _remove_prefix(parsed_dsn.path, "/")
        return values


class BotSettings(pydantic.BaseModel):
    token: str


class KinopoiskSettings(pydantic.BaseModel):
    base_url: str = "https://kinopoiskapiunofficial.tech/"
    api_key: str


class Settings(pydantic_settings.BaseSettings):
    run_migrations_on_startup: int = 1

    postgres: PostgresSettings
    bot: BotSettings
    kinopoisk: KinopoiskSettings

    log_level: str = pydantic.Field(
        default="INFO",
        description="Желательно не использовать DEBUG в логах, кроме случаев локальной отладки",
    )
    log_config_path: pathlib.Path | None = pydantic.Field(
        default=None,
        description="Путь к конфигурации логирования в формате YAML",
    )

    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=("conf/.env", os.getenv("ENV_FILE", ".env")),
        env_file_encoding="utf-8",
    )

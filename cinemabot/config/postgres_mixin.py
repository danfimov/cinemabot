from os import environ

from pydantic import BaseSettings


class PostgresMixin(BaseSettings):
    DB_NAME: str = environ.get("POSTGRES_DB", "cinemabot_db")
    DB_PATH: str = environ.get("POSTGRES_PATH", "localhost")
    DB_USER: str = environ.get("POSTGRES_USER", "cinemabot_admin")
    DB_PORT: int = 5432
    DB_PASSWORD: str = environ.get("POSTGRES_PASSWORD", "password")
    SSL_MODE: str = "disable"
    DB_POOL_SIZE: int = 15
    DB_CONNECT_RETRY: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def db_settings(self) -> dict[str, str | int]:
        return {
            "database": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_PATH,
            "port": self.DB_PORT,
            "ssl_mode": self.SSL_MODE,
        }

    @property
    def database_url(self) -> str:
        return ("postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}" "?ssl={ssl_mode}&prepared_statement_cache_size=0").format(**self.db_settings)

    @property
    def database_url_for_sync_connection(self) -> str:
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**self.db_settings)

    @property
    def multihost_database_url(self) -> str:
        hosts = ",".join(f'{host}:{self.db_settings["port"]}' for host in self.db_settings["host"].split(",")).replace(" ", "")  # type: ignore
        return "postgresql://{user}:{password}@{hosts}/{database}".format(
            hosts=hosts,
            **self.db_settings,
        )

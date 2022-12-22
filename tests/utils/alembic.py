from os import path as os_path
from pathlib import Path

from alembic.config import Config
from configargparse import Namespace

from cinemabot.config import get_settings


PROJECT_PATH = Path(__file__).parent.parent.parent.resolve()


def make_alembic_config(cmd_opts: Namespace, base_path: Path = PROJECT_PATH) -> Config:
    """
    Создает объект конфигурации alembic на основе аргументов командной строки,
    подменяет относительные пути на абсолютные.
    """
    database_uri = get_settings().database_url_for_sync_connection

    path_to_folder = cmd_opts.config
    # Подменяем путь до файла alembic.ini на абсолютный
    if not os_path.isabs(cmd_opts.config):
        cmd_opts.config = os_path.join(base_path, cmd_opts.config + "alembic.ini")

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Подменяем путь до папки с alembic на абсолютный
    alembic_location = config.get_main_option("script_location")
    if not os_path.isabs(alembic_location):  # type: ignore
        config.set_main_option("script_location", os_path.join(base_path, path_to_folder + alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", database_uri)

    return config

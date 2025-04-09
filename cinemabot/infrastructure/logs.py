import logging.config
from pathlib import Path
from typing import Optional, Union

import yaml


def configure_logging(
    path_to_log_config: Optional[Path] = None,
    root_level: Union[str, int, None] = None,
) -> None:
    """Функция для настройки логирования с помощью конфигурационного yaml файла."""
    if not path_to_log_config:
        logging.basicConfig(level=root_level or logging.DEBUG)
        return
    with Path(path_to_log_config).open("r") as file:
        loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)
    if root_level:
        logging.root.setLevel(root_level)

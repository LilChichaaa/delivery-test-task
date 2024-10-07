import logging
import logging.config as logging_config
import os
import json

from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['config.json'])


def setup_logging(default_path: str = 'logging_config.json', default_level: int = logging.INFO):
    """
    Настройка логгера из JSON-файла конфигурации.

    :param default_path: Путь к файлу конфигурации.
    :param default_level: Уровень логирования по умолчанию, если файл конфигурации не найден.
    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt', encoding='utf-8') as f:
            config = json.load(f)
        logging_config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print(f"Файл конфигурации {default_path} не найден. Используется базовое логирование.")

import sys
import os
import json
from fastapi import FastAPI
from loguru import logger

logger.remove()  # Удаляем все существующие хэндлеры для того, чтобы настроить новый
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True,
    colorize=True,
    backtrace=True,
    diagnose=True,
    enqueue=True
)

app = FastAPI(
    title="International Delivery API",
    description="API для управления международной доставкой посылок. Вы можете регистрировать посылки, управлять ими, а также привязывать их к транспортным компаниям.",
    version="1.0.0",
    contact={
        "name": "Roman Mamin",
        "url": "https://t.me/mamin_boec",
        "email": "roman74mamin@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://example.com/license/",
    }
)

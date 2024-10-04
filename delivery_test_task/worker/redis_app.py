import redis
import requests

from typing import Union
from .. import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)


def get_cached_usd_rate() -> Union[int, None]:
    """Получение курса USD из Redis"""

    cached_rate = redis_client.get(settings.USD_RATE_KEY)

    if cached_rate:
        print(f"Курс USD из кэша Redis: {cached_rate.decode('utf-8')}")
    else:
        print("Курс USD не найден в кэше Redis.")

    return cached_rate

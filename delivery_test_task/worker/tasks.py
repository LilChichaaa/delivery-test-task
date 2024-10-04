import json
import requests
import redis

from typing import Union
from .. import settings

from .redis_app import redis_client

from .celery_app import celery_app


@celery_app.task
def check_dollar_exchange_rate():
    """Получение курса USD"""

    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    # Выполнение запроса
    response = requests.get(url)

    # Проверка успешности запроса
    if response.status_code == 200:
        data = response.json()

        # Извлечение значения USD.Value
        usd_rate = data['Valute']['USD']['Value']
        print(f"Текущий курс USD: {usd_rate}")

        # Кэширование значения в Redis
        redis_client.set(settings.USD_RATE_KEY, usd_rate)
        print(f"Курс USD успешно сохранен в Redis.")
        return usd_rate
    else:
        print(f"Ошибка при выполнении запроса: {response.status_code}")

import json
import requests
import redis
import asyncio

from typing import Union
from .. import settings

from .redis_app import redis_client

from .celery_app import celery_app

from ..models.database import get_db
from ..models.sqlalchemy_models import Parcel
from ..models.pydantic_models import ParcelCreate

@celery_app.task
def check_dollar_exchange_rate() -> float:
    """Получение курса USD"""

    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    response = requests.get(url)

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
        check_dollar_exchange_rate.delay()
        print(f"Ошибка при выполнении запроса: {response.status_code}")

@celery_app.task
def get_cached_usd_rate() -> Union[float, None]:
    """Получение курса USD из Redis"""

    cached_rate = redis_client.get(settings.USD_RATE_KEY)

    if cached_rate:
        print(f"Курс USD из кэша Redis: {cached_rate.decode('utf-8')}")
    else:
        print("Курс USD не найден в кэше Redis.")

    return float(cached_rate.decode('utf-8')) if cached_rate is not None else cached_rate


@celery_app.task
def register_parcel(parcel: dict, user_id: str) -> None:
    """Запуск асинхронной регистрации посылки"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Создаем новый event loop, если его нет
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Если loop уже запущен, используем ensure_future для создания задачи
    if loop.is_running():
        asyncio.ensure_future(register_parcel_async(parcel, user_id))
    else:
        # Если event loop не запущен, запускаем его через run_until_complete
        loop.run_until_complete(register_parcel_async(parcel, user_id))


async def register_parcel_async(parcel: dict, user_id: str) -> None:
    """Асинхронная регистрация посылки"""
    async for db in get_db():
        parcel = await Parcel.create(db, parcel_data=ParcelCreate(**parcel), user_id=user_id)

        usd_rate = get_cached_usd_rate()
        if usd_rate:
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)
        else:
            usd_rate = check_dollar_exchange_rate()
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)

        await db.commit()

def count_delivery_cost(parcel: Parcel, usd_rate: float):
    return  (parcel.weight * 0.5 + parcel.value*0.01)*usd_rate





import json
import requests
import redis
import asyncio
import aiohttp

from typing import Union
from .. import settings

from .redis_app import redis_client

from .celery_app import celery_app

from ..models.database import get_db
from ..models.sqlalchemy_models import Parcel
from ..models.pydantic_models import ParcelCreate


def run_async_task(async_func, *args, **kwargs):
    """Helper function to run an async function in a Celery task."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        asyncio.ensure_future(async_func(*args, **kwargs))
    else:
        loop.run_until_complete(async_func(*args, **kwargs))

@celery_app.task
def register_parcel(parcel: dict, user_id: str) -> None:
    """Celery task to register a parcel asynchronously."""
    run_async_task(register_parcel_async, parcel, user_id)

@celery_app.task
def check_dollar_exchange_rate() -> None:
    """Celery task to register a parcel asynchronously."""
    run_async_task(check_dollar_exchange_rate_async)


async def check_dollar_exchange_rate_async() -> float:
    """Асинхронное получение курса USD"""
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json(content_type=None)

                # Извлечение значения USD.Value
                usd_rate = data['Valute']['USD']['Value']
                print(f"Текущий курс USD: {usd_rate}")

                # Кэширование значения в Redis
                await redis_client.set(settings.USD_RATE_KEY, usd_rate)
                print(f"Курс USD успешно сохранен в Redis.")
                return usd_rate
            else:
                print(f"Ошибка при выполнении запроса: {response.status}")
                raise Exception(f"Не удалось получить курс USD, статус {response.status}")

async def get_cached_usd_rate() -> Union[float, None]:
    """Получение курса USD из Redis"""

    cached_rate = await redis_client.get(settings.USD_RATE_KEY)

    if cached_rate:
        print(f"Курс USD из кэша Redis: {cached_rate.decode('utf-8')}")
    else:
        print("Курс USD не найден в кэше Redis.")

    return float(cached_rate.decode('utf-8')) if cached_rate is not None else cached_rate



async def register_parcel_async(parcel: dict, user_id: str) -> None:
    """Асинхронная регистрация посылки"""
    async for db in get_db():
        parcel = await Parcel.create(db, parcel_data=ParcelCreate(**parcel), user_id=user_id)

        usd_rate = await get_cached_usd_rate()
        if usd_rate:
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)
        else:
            usd_rate = await check_dollar_exchange_rate_async()
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)

        await db.commit()

def count_delivery_cost(parcel: Parcel, usd_rate: float):
    return  (parcel.weight * 0.5 + parcel.value*0.01)*usd_rate





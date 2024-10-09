import sys
import asyncio
import aiohttp

from typing import Union
from .. import settings

from .redis_app import redis_client
from .celery_app import celery_app
from ..models.database import get_db
from ..models.sqlalchemy_models import Parcel
from ..models.pydantic_models import ParcelCreate
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


def run_async_task(async_func, *args, **kwargs) -> None:
    """
    Помощник для запуска асинхронной функции внутри задачи Celery.

    Если событийный цикл уже запущен, планирует выполнение корутины.
    В противном случае запускает событийный цикл и выполняет корутину.

    Параметры:
    - async_func: Асинхронная функция для выполнения.
    - *args, **kwargs: Аргументы для передачи в асинхронную функцию.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        logger.debug("Создание нового event loop, так как текущий отсутствует")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        logger.debug(f"Запуск корутины {async_func.__name__} в существующем event loop")
        asyncio.ensure_future(async_func(*args, **kwargs))
    else:
        logger.debug(f"Запуск корутины {async_func.__name__} в новом event loop")
        loop.run_until_complete(async_func(*args, **kwargs))


@celery_app.task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 20},
    retry_backoff=True,
    retry_backoff_max=30,
    retry_jitter=True
)
def register_parcel(parcel: dict, user_id: str) -> None:
    """
    Задача Celery для асинхронной регистрации посылки.

    Параметры:
    - parcel: Словарь с данными посылки.
    - user_id: Идентификатор пользователя.
    """
    logger.info(f"Запуск задачи регистрации посылки для пользователя {user_id}")
    run_async_task(register_parcel_async, parcel, user_id)


@celery_app.task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 20},
    retry_backoff=True,
    retry_backoff_max=30,
    retry_jitter=True
)
def check_dollar_exchange_rate() -> None:
    """
    Задача Celery для асинхронного обновления курса доллара.

    Запускает асинхронную функцию для получения текущего курса USD и сохранения его в Redis.
    """
    logger.info("Запуск задачи получения курса доллара")
    run_async_task(check_dollar_exchange_rate_async)


async def check_dollar_exchange_rate_async() -> float:
    """
    Асинхронное получение текущего курса USD и сохранение его в Redis.

    Делает запрос к API Центробанка России для получения текущего курса USD.
    Кэширует полученное значение в Redis.

    Возвращает:
    - usd_rate: Текущий курс USD в виде числа с плавающей запятой.
    """
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)

                    # Извлечение значения USD.Value
                    usd_rate = data['Valute']['USD']['Value']
                    logger.info(f"Текущий курс USD: {usd_rate}")

                    # Кэширование значения в Redis
                    await redis_client.set(settings.USD_RATE_KEY, usd_rate)
                    logger.info("Курс USD успешно сохранен в Redis")
                    return usd_rate
                else:
                    raise Exception(f"Не удалось получить курс USD, статус {response.status}")
    except Exception as e:
        logger.exception("Ошибка при получении курса USD")
        raise


async def get_cached_usd_rate() -> Union[float, None]:
    """
    Асинхронное получение курса USD из Redis.

    Возвращает:
    - usd_rate: Курс USD в виде числа с плавающей запятой, если он есть в кэше.
    - None: Если курса нет в кэше.
    """
    try:
        cached_rate = await redis_client.get(settings.USD_RATE_KEY)

        if cached_rate:
            usd_rate = cached_rate.decode('utf-8')
            logger.info(f"Курс USD из кэша Redis: {usd_rate}")
            return float(usd_rate)
        else:
            logger.warning("Курс USD не найден в кэше Redis")
            return None
    except Exception as e:
        logger.exception("Ошибка при попытке получить курс USD из Redis")
        raise


async def register_parcel_async(parcel: dict, user_id: str) -> None:
    """
    Асинхронная регистрация посылки в базе данных с вычислением стоимости доставки.

    Параметры:
    - parcel: Словарь с данными посылки.
    - user_id: Идентификатор пользователя.

    Процесс:
    1. Создает новую запись посылки в базе данных.
    2. Пытается получить курс USD из кэша Redis.
    3. Если курс не найден в кэше, запрашивает текущий курс и сохраняет его в кэш.
    4. Вычисляет стоимость доставки на основе веса, стоимости посылки и курса USD.
    5. Сохраняет обновленную информацию о посылке в базе данных.
    """
    logger.info(f"Регистрация посылки для пользователя {user_id}")
    async for db in get_db():
        parcel = await Parcel.create(db, parcel_data=ParcelCreate(**parcel), user_id=user_id)

        usd_rate = await get_cached_usd_rate()
        if usd_rate:
            logger.debug(f"Курс USD получен: {usd_rate}")
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)
        else:
            logger.info("Курс USD не найден в кэше, запрашиваем текущий курс")
            usd_rate = await check_dollar_exchange_rate_async()
            parcel.delivery_cost = count_delivery_cost(parcel, usd_rate)

        await db.commit()
        logger.info(f"Посылка {parcel.id} зарегистрирована с стоимостью доставки {parcel.delivery_cost}")


def count_delivery_cost(parcel: Parcel, usd_rate: float) -> float:
    """
    Вычисление стоимости доставки посылки.

    Параметры:
    - parcel: Объект посылки.
    - usd_rate: Текущий курс USD.

    Возвращает:
    - Стоимость доставки в виде числа с плавающей запятой.
    """
    cost = (parcel.weight * 0.5 + parcel.value * 0.01) * usd_rate
    logger.debug(f"Стоимость доставки: {cost} для посылки {parcel.id}")
    return cost

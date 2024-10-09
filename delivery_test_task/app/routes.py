import uuid
import logging
import sys

from typing import Optional
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, Cookie, Response, Request

from .swagger import registration, parcel_types, parcels, parcels_num, parcel_asign_company, usd

from .main import app
from ..models.pydantic_models import ParcelCreate, ParcelTypeOut, ParcelOut, ParcelList

from ..models.database import get_db

from ..models.sqlalchemy_models import Parcel, ParcelType

from ..worker.tasks import check_dollar_exchange_rate, register_parcel
from loguru import logger

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware для логирования запросов"""
    try:

        logger.info(f"Запрос: {request.method} {request.url}")

        body = await request.body()
        logger.info(f"Тело запроса: {body.decode('utf-8')}")
        if body:
            logger.info(f"Тело запроса: {body.decode('utf-8')}")

        response = await call_next(request)
        return response
    except Exception:
        import traceback
        traceback.print_exc()

def run_migrations():
    """Применение миграций Alembic при старте приложения"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def get_user_id(user_id: Optional[str] = Cookie(None), response: Response = None):
    """
    Получение и генерация user_id из/в cookie
    """
    if user_id is None:
        user_id = str(uuid.uuid4())
        response.set_cookie(key="user_id", value=user_id)
    return user_id


@app.on_event("startup")
async def on_startup():
    """Этот код выполняется при запуске приложения FastAPI для применения миграций"""
    print("Применение миграций...")
    run_migrations()
    print("Миграции выполнены")


@app.get("/dollar-exchange-rate", response_model=dict, tags=["Debug"], summary="Получение курса USD",
          description="Принудительно получает курс USD и возвращает id celery задачи", responses=usd)
async def dollar_exchange_rate():
    """
    Принудительно получает текущий курс USD

    Возвращает id Celery-задачи
    """
    return {"task_id": check_dollar_exchange_rate.delay().id}

@app.post("/parcel-registration", response_model=dict, tags=["Parcel Management"], summary="Регистрация посылки",
          description="Регистрирует новую посылку и возвращает уникальный идентификатор.",
          responses=registration)
async def parcel_registration(
        parcel: ParcelCreate,
        # db: AsyncSession = Depends(get_db),
        user_id: str = Depends(get_user_id)
):
    """
    Регистрирует новую посылку.

    - **name**: Название посылки
    - **weight**: Вес посылки в кг
    - **value**: Стоимость содержимого в долларах
    - **parcel_type_id**: Идентификатор типа посылки (одежда, электроника и т.д.)

    Возвращает уникальный ID посылки для текущей сессии пользователя.
    """

    return {"task_id": register_parcel.delay(parcel.dict(), user_id).id}


@app.get("/parcel-types", response_model=list[ParcelTypeOut], tags=["Parcel Management"],
         summary="Получить все типы посылок", description="Возвращает список всех типов посылок и их идентификаторов.",
         responses=parcel_types)
async def get_parcel_types(db: AsyncSession = Depends(get_db)):
    """
    Возвращает все доступные типы посылок с их идентификаторами:

    - Documents
    - Electronics
    - Clothing
    """
    parcel_types = await ParcelType.get_all_types(db)

    return parcel_types


@app.get("/parcels", response_model=ParcelList, tags=["Parcel Management"], summary="Получить список посылок",
         description="Возвращает список посылок с фильтрацией и пагинацией на основе номеров страниц.",
         responses=parcels)
async def get_parcels(
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
        parcel_type_id: Optional[int] = None,
        has_delivery_cost: Optional[bool] = None,
        db: AsyncSession = Depends(get_db),
        user_id: str = Depends(get_user_id)
):
    """
    Возвращает список посылок с поддержкой пагинации и фильтрации:

    - **page**: Номер страницы (начиная с 1)
    - **page_size**: Количество записей на странице
    - **parcel_type_id**: Фильтр по типу посылки
    - **has_delivery_cost**: Фильтр по наличию рассчитанной стоимости доставки (True/False)

    Возвращает:
    - **parcels**: Список посылок
    - **total**: Общее количество посылок
    """
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Page and page_size must be positive integers.")

    skip = (page - 1) * page_size

    parcels, total = await Parcel.get_all(db, skip=skip, limit=page_size, parcel_type_id=parcel_type_id,
                                          has_delivery_cost=has_delivery_cost, user_id=user_id)

    result = [
        ParcelOut(
            id=p.id,
            name=p.name,
            weight=p.weight,
            value=p.value,
            parcel_type=p.parcel_type.name,
            delivery_cost=p.delivery_cost
        ) for p in parcels
    ]

    return ParcelList(parcels=result, total=total)


@app.get("/parcels/{parcel_id}", response_model=ParcelOut, tags=["Parcel Management"],
         summary="Получить информацию о посылке",
         description="Возвращает данные о посылке по её уникальному идентификатору.",
         responses=parcels_num)
async def get_parcel(parcel_id: int,
                     db: AsyncSession = Depends(get_db),
                     user_id: str = Depends(get_user_id)):
    """
    Получить информацию о посылке по её ID:

    - **parcel_id**: Уникальный идентификатор посылки

    Возвращает:
    - **id**: Идентификатор посылки
    - **name**: Название посылки
    - **weight**: Вес посылки
    - **value**: Стоимость посылки
    - **parcel_type**: Тип посылки
    - **delivery_cost**: Стоимость доставки (если рассчитана)
    """
    parcel = await Parcel.get_by_id(db, parcel_id, user_id=user_id)

    return ParcelOut(
        id=parcel.id,
        name=parcel.name,
        weight=parcel.weight,
        value=parcel.value,
        parcel_type=parcel.parcel_type.name,
        delivery_cost=parcel.delivery_cost
    )


@app.post("/parcels/{parcel_id}/assign-company", response_model=dict, tags=["Parcel Management"],
          summary="Привязать посылку к транспортной компании",
          description="Привязывает посылку к указанной транспортной компании.",
          responses=parcel_asign_company)
async def assign_company(parcel_id: int, company_id: int,
                         db: AsyncSession = Depends(get_db),
                         user_id: str = Depends(get_user_id)):
    """
    Привязывает посылку к транспортной компании.

    - **parcel_id**: Уникальный идентификатор посылки
    - **company_id**: Уникальный идентификатор транспортной компании

    Возвращает сообщение о результате операции.
    """
    await Parcel.assign_company(db, parcel_id=parcel_id, company_id=company_id, user_id=user_id)

    return {"message": "Company assigned successfully"}

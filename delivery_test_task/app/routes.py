from typing import Optional
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse

from .main import app

from ..models.pydantic_models import ParcelCreate, ParcelTypeOut, ParcelOut, ParcelList

from ..models.database import get_db

from ..models.sqlalchemy_models import Parcel, ParcelType


def run_migrations():
    """Применение миграций Alembic"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@app.on_event("startup")
async def on_startup():
    """Этот код выполняется при запуске приложения FastAPI"""
    print("Применение миграций...")
    run_migrations()
    print("Миграции выполнены")


@app.post("/parcel-registration", response_model=dict)
async def parcel_registration(parcel: ParcelCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрирует новую посылку.

    Возвращает уникальный id посылки для сессии пользователя.
    """
    parcel_id = await Parcel.create(db, parcel_data=parcel)

    return {"id": parcel_id}



# 2. Получить все типы посылок и их ID
@app.get("/parcel-types", response_model=list[ParcelTypeOut])
async def get_parcel_types(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех типов посылок и их идентификаторы.
    """
    parcel_types = await ParcelType.get_all_types(db)

    return parcel_types


# 3. Получить список своих посылок с пагинацией и фильтрацией
@app.get("/parcels", response_model=ParcelList)
async def get_parcels(
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
        parcel_type_id: Optional[int] = None,
        has_delivery_cost: Optional[bool] = None,
        db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список посылок пользователя с фильтрацией и пагинацией на основе номеров страниц.
    """
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Page and page_size must be positive integers.")

    # Расчет количества записей для пропуска на основе текущей страницы
    skip = (page - 1) * page_size

    parcels, total = await Parcel.get_all(db, skip=skip, limit=page_size, parcel_type_id=parcel_type_id,
                                          has_delivery_cost=has_delivery_cost)

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


# 4. Получить данные о посылке по ее ID
@app.get("/parcels/{parcel_id}", response_model=ParcelOut)
async def get_parcel(parcel_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные о посылке по ее уникальному идентификатору.
    """
    parcel = await Parcel.get_by_id(db, parcel_id)

    return ParcelOut(
            id=parcel.id,
            name=parcel.name,
            weight=parcel.weight,
            value=parcel.value,
            parcel_type=parcel.parcel_type.name,
            delivery_cost=parcel.delivery_cost
    )


@app.post("/parcels/{parcel_id}/assign-company", response_model=dict)
async def assign_company(parcel_id: int, company_id: int, db: AsyncSession = Depends(get_db)):
    """
    Привязывает посылку к транспортной компании.
    """
    await Parcel.assign_company(db, parcel_id=parcel_id, company_id=company_id)

    return {"message": "Company assigned successfully"}

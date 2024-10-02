from typing import Optional
from alembic import command
from alembic.config import Config


from .main import app

from ..models.pydantic_models import ParcelCreate, ParcelTypeOut, ParcelOut, ParcelList


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

@app.post("/parcel-registration", response_model=int)
async def parcel_registration(parcel: ParcelCreate):
    """
    Регистрирует новую посылку.

    Возвращает id посылки.
    """
    return {"id": 1}

# 2. Получить все типы посылок и их ID
@app.get("/parcel-types", response_model=list[ParcelTypeOut])
async def get_parcel_types():
    """
    Возвращает список всех типов посылок и их идентификаторы.
    """
    types = [
        {"id": 1, "name": "Одежда"},
        {"id": 2, "name": "Электроника"},
        {"id": 3, "name": "Разное"}
    ]
    return types  # Здесь будет реализована логика получения типов посылок

# 3. Получить список своих посылок с пагинацией и фильтрацией
@app.get("/parcels", response_model=ParcelList)
async def get_parcels(
    skip: int = 0,
    limit: int = 10,
    parcel_type_id: Optional[int] = None,
    has_delivery_cost: Optional[bool] = None
):
    """
    Возвращает список посылок пользователя со всеми полями,
    включая название типа посылки и стоимость доставки (если она рассчитана).

    Параметры запроса:
    - skip: Сколько записей пропустить (для пагинации).
    - limit: Максимальное количество записей для возврата.
    - parcel_type_id: Фильтр по типу посылки.
    - has_delivery_cost: Фильтр по наличию рассчитанной стоимости доставки.
    """
    parcels = [
        {
            "id": 1,
            "name": "Laptop",
            "weight": 2.5,
            "value": 1500,
            "parcel_type": "Электроника",
            "delivery_cost": 50.0
        }
    ]
    return {"parcels": parcels, "total": 1}

# 4. Получить данные о посылке по ее ID
@app.get("/parcels/{parcel_id}", response_model=ParcelOut)
async def get_parcel(parcel_id: int):
    """
    Возвращает данные о посылке по ее уникальному идентификатору.

    Возвращаемые данные:
    - Название
    - Вес
    - Тип посылки
    - Стоимость содержимого
    - Стоимость доставки
    """
    parcel = {
        "id": parcel_id,
        "name": "Laptop",
        "weight": 2.5,
        "value": 1500,
        "parcel_type": "Электроника",
        "delivery_cost": 50.0
    }
    return parcel  # Здесь будет реализована логика получения данных о конкретной посылке
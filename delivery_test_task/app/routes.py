from typing import Optional

from .main import app, router

from ..models.pydantic_models import ParcelCreate, ParcelTypeOut, ParcelOut, ParcelList

@router.get("/")
def read_root():
    return {"message": "Hello, World!"}

@router.post("/register_parcel", response_model=int)
async def register_parcel(parcel: ParcelCreate):
    """
    Регистрирует новую посылку.

    Возвращает id посылки.
    """
    return 1

# 2. Получить все типы посылок и их ID
@router.get("/parcel_types", response_model=list[ParcelTypeOut])
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
@router.get("/parcels", response_model=ParcelList)
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
@router.get("/parcels/{parcel_id}", response_model=ParcelOut)
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

app.include_router(router)
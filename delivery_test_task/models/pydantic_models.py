from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union


class ParcelCreate(BaseModel):
    """
    Модель для создания новой посылки.
    """
    name: str = Field(..., example="Laptop", description="Название посылки")
    weight: float = Field(..., gt=0, example=2.5, description="Вес посылки в килограммах, должен быть больше 0")
    value: float = Field(..., gt=0, example=1500, description="Стоимость содержимого в долларах, должна быть больше 0")
    parcel_type_id: int = Field(..., example=2,
                                description="Идентификатор типа посылки (например, 1 - Одежда, 2 - Электроника)")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, name: str):
        """
        Валидатор, проверяющий, что название посылки не пустое.
        """
        if not name.strip():
            raise ValueError('Название не может быть пустым')
        return name


class ParcelOut(BaseModel):
    """
    Модель для вывода информации о посылке.
    """
    id: int = Field(..., example=123, description="Уникальный идентификатор посылки")
    name: str = Field(..., example="Laptop", description="Название посылки")
    weight: float = Field(..., example=2.5, description="Вес посылки в килограммах")
    value: float = Field(..., example=1500, description="Стоимость содержимого в долларах")
    parcel_type: str = Field(..., example="Электроника",
                             description="Название типа посылки (Одежда, Электроника, и т.д.)")
    delivery_cost: Optional[Union[float, str]] = Field(
        None, example="Не рассчитано",
        description="Стоимость доставки. Может быть числом или строкой 'Не рассчитано', если стоимость не была рассчитана"
    )

    @field_validator('delivery_cost', mode='before')
    @classmethod
    def set_default_delivery_cost(cls, v):
        """
        Валидатор, который устанавливает значение "Не рассчитано", если поле `delivery_cost` пустое.
        """
        if v is None:
            return "Не рассчитано"
        return v


class ParcelTypeOut(BaseModel):
    """
    Модель для вывода информации о типе посылки.
    """
    id: int = Field(..., example=1, description="Уникальный идентификатор типа посылки")
    name: str = Field(..., example="Одежда", description="Название типа посылки (например, Одежда, Электроника)")


class ParcelList(BaseModel):
    """
    Модель для вывода списка посылок с поддержкой пагинации.
    """
    parcels: list[ParcelOut] = Field(..., description="Список всех посылок")
    total: int = Field(..., example=100, description="Общее количество посылок")




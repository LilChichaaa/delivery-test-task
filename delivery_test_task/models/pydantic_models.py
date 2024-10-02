from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union

class ParcelCreate(BaseModel):
    name: str = Field(..., example="Laptop", description="Название посылки")
    weight: float = Field(..., gt=0, example=2.5, description="Вес посылки в кг")
    value: float = Field(..., gt=0, example=1500, description="Стоимость содержимого в долларах")
    parcel_type_id: int = Field(..., example=2, description="Идентификатор типа посылки")


    @field_validator('name')
    @classmethod
    def name_not_empty(cls, name: str):
        if not name.strip():
            raise ValueError('Название не может быть пустым')
        return name

class ParcelOut(BaseModel):
    id: int
    name: str
    weight: float
    value: float
    parcel_type: str
    delivery_cost: Optional[Union[float, str]] = None

    @field_validator('delivery_cost', mode='before')
    @classmethod
    def set_default_delivery_cost(cls, v):
        if v is None:
            return "Не рассчитано"
        return v

class ParcelTypeOut(BaseModel):
    id: int
    name: str

class ParcelList(BaseModel):
    parcels: list[ParcelOut]
    total: int



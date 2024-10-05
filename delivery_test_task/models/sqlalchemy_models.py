from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .database import Base
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.sql import func

class ParcelType(Base):
    __tablename__ = 'parcel_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    parcels = relationship("Parcel", back_populates="parcel_type")

    @classmethod
    async def get_all_types(cls, db: AsyncSession):
        """Возвращает список всех типов посылок"""
        result = await db.execute(select(cls))
        return result.scalars().all()

class Parcel(Base):
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    delivery_cost = Column(Float, nullable=True)

    user_id = Column(String, nullable=False)

    transport_company_id = Column(Integer, ForeignKey('transport_companies.id'), nullable=True)
    parcel_type_id = Column(Integer, ForeignKey('parcel_types.id'), nullable=False)
    parcel_type = relationship("ParcelType", back_populates="parcels")
    transport_company = relationship("TransportCompany", back_populates="parcels")

    __table_args__ = (
        UniqueConstraint('id', 'transport_company_id', name='uix_parcel_company'),
    )

    @classmethod
    async def create(cls, db: AsyncSession, parcel_data, user_id: str):
        """Создает новую посылку и сохраняет в БД"""
        new_parcel = cls(
            name=parcel_data.name,
            weight=parcel_data.weight,
            value=parcel_data.value,
            parcel_type_id=parcel_data.parcel_type_id,
            user_id = user_id
        )
        db.add(new_parcel)
        try:
            await db.commit()
            await db.refresh(new_parcel)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Parcel creation failed due to integrity error.")
        return new_parcel

    @classmethod
    async def get_all(cls, db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10, parcel_type_id: int = None,
                      has_delivery_cost: bool = None):
        """Возвращает список всех посылок с фильтрацией и пагинацией"""

        # Стартовый запрос с загрузкой связанных данных
        stmt = select(cls).where(cls.user_id == user_id).options(selectinload(cls.parcel_type))

        # Применение фильтров по типу посылки и стоимости доставки
        if parcel_type_id:
            stmt = stmt.where(cls.parcel_type_id == parcel_type_id)

        if has_delivery_cost is not None:
            if has_delivery_cost:
                stmt = stmt.where(cls.delivery_cost.isnot(None))
            else:
                stmt = stmt.where(cls.delivery_cost.is_(None))

        # Сначала подсчитываем общее количество отфильтрованных записей
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(total_stmt)
        total = total_result.scalar()

        # Применение пагинации к отфильтрованному результату
        stmt = stmt.offset(skip).limit(limit)

        # Выполнение запроса и получение данных
        result = await db.execute(stmt)
        parcels = result.scalars().all()

        return parcels, total

    @classmethod
    async def get_by_id(cls, db: AsyncSession, parcel_id: int, user_id: str):
        """Получает посылку по ID с загрузкой типа посылки"""
        stmt = select(cls).options(selectinload(cls.parcel_type)).where(cls.id == parcel_id).where(cls.user_id == user_id)
        result = await db.execute(stmt)
        parcel = result.scalar_one_or_none()

        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")
        return parcel

    @classmethod
    async def assign_company(cls, db: AsyncSession, parcel_id: int, company_id: int, user_id: str):
        """Привязывает посылку к транспортной компании с блокировкой"""
        try:
            async with db.begin():
                # Выполняем запрос с блокировкой строки
                stmt = select(cls).where(cls.id == parcel_id).where(cls.user_id == user_id).with_for_update()
                result = await db.execute(stmt)
                parcel = result.scalar_one_or_none()

                if not parcel:
                    raise HTTPException(status_code=404, detail="Parcel not found")

                if parcel.transport_company_id:
                    raise HTTPException(status_code=400, detail="Parcel already assigned to a transport company")

                parcel.transport_company_id = company_id
                db.add(parcel)

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Company assignment failed due to integrity error.")

        except OperationalError as e:
            # Обработка блокировок и таймаутов
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database operation failed due to concurrency issues.")

        return parcel

class TransportCompany(Base):
    __tablename__ = 'transport_companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    parcels = relationship("Parcel", back_populates="transport_company")


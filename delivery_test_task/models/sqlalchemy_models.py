from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class ParcelType(Base):
    __tablename__ = 'parcel_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    parcels = relationship("Parcel", back_populates="parcel_type")

class Parcel(Base):
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    parcel_type_id = Column(Integer, ForeignKey('parcel_types.id'), nullable=False)
    delivery_cost = Column(Float, nullable=True)  # Стоимость доставки, если рассчитана
    transport_company_id = Column(Integer, nullable=True)  # ID транспортной компании

    parcel_type = relationship("ParcelType", back_populates="parcels")

    __table_args__ = (
        UniqueConstraint('id', 'transport_company_id', name='uix_parcel_company'),
    )

class TransportCompany(Base):
    __tablename__ = 'transport_companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    parcels = relationship("Parcel", back_populates="transport_company")


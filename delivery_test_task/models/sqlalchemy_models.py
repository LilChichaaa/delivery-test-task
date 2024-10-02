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
    delivery_cost = Column(Float, nullable=True)

    transport_company_id = Column(Integer, ForeignKey('transport_companies.json.id'), nullable=True)
    parcel_type_id = Column(Integer, ForeignKey('parcel_types.id'), nullable=False)
    parcel_type = relationship("ParcelType", back_populates="parcels")
    transport_company = relationship("TransportCompany", back_populates="parcels")

    __table_args__ = (
        UniqueConstraint('id', 'transport_company_id', name='uix_parcel_company'),
    )

class TransportCompany(Base):
    __tablename__ = 'transport_companies.json'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    parcels = relationship("Parcel", back_populates="transport_company")


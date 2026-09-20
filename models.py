from sqlalchemy import Column, Integer, String, Float
from database import Base


class FurnitureProduct(Base):
    __tablename__ = "furniture_products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    category = Column(String(100), nullable=False)

    price = Column(Integer, nullable=False)

    image_filename = Column(String(255), nullable=False)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)

    image_filename = Column(String(255), nullable=False)

class DetectedObject(Base):
    __tablename__ = "detected_objects"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(Integer, nullable=False)

    object_name = Column(String(100), nullable=False)

    confidence = Column(Float, nullable=False)

    recommendation_name = Column(String(255), nullable=True)

    recommendation_price = Column(Integer, nullable=True)
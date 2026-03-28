from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False, index=True)
    floor = Column(Integer, nullable=True)
    building = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    qr_token = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name_th = Column(String, nullable=False, index=True)
    name_en = Column(String, nullable=True)
    description_th = Column(String, nullable=True)
    description_en = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    is_promotion = Column(Boolean, default=False, nullable=False)
    promo_price = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)    

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False, index=True)
    status = Column(String, default="new", nullable=False)
    total_amount = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    menu_item_id = Column(Integer, nullable=False, index=True)
    qty = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    line_total = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
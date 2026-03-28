from pydantic import BaseModel


class RoomCreate(BaseModel):
    room_number: str
    floor: int | None = None
    building: str | None = None
    status: str = "active"
    qr_token: str

class MenuItemCreate(BaseModel):
    name_th: str
    name_en: str | None = None
    description_th: str | None = None
    description_en: str | None = None
    price: int
    image_url: str | None = None
    is_available: bool = True
    is_promotion: bool = False
    promo_price: int | None = None    

class OrderItemCreate(BaseModel):
    menu_item_id: int
    qty: int


class OrderCreate(BaseModel):
    qr_token: str
    items: list[OrderItemCreate]    

class OrderStatusUpdate(BaseModel):
    status: str    
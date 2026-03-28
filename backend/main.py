from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine, get_db, test_db_connection
from models import Base, MenuItem, Order, OrderItem, Room
from schemas import MenuItemCreate, OrderCreate, OrderStatusUpdate, RoomCreate
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hotel F&B System Running"}


@app.get("/test")
def test():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    result = test_db_connection()
    return {"database": "connected", "result": result}


@app.post("/rooms")
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    try:
        new_room = Room(
            room_number=room.room_number,
            floor=room.floor,
            building=room.building,
            status=room.status,
            qr_token=room.qr_token,
            is_active=True,
        )

        db.add(new_room)
        db.commit()
        db.refresh(new_room)

        return {
            "message": "Room created successfully",
            "room": {
                "id": new_room.id,
                "room_number": new_room.room_number,
                "floor": new_room.floor,
                "building": new_room.building,
                "status": new_room.status,
                "qr_token": new_room.qr_token,
                "is_active": new_room.is_active,
            },
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e.orig)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).order_by(Room.id.asc()).all()

    return [
        {
            "id": room.id,
            "room_number": room.room_number,
            "floor": room.floor,
            "building": room.building,
            "status": room.status,
            "qr_token": room.qr_token,
            "is_active": room.is_active,
        }
        for room in rooms
    ]    
    
@app.post("/menu-items")
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    try:
        new_menu_item = MenuItem(
            name_th=menu_item.name_th,
            name_en=menu_item.name_en,
            description_th=menu_item.description_th,
            description_en=menu_item.description_en,
            price=menu_item.price,
            image_url=menu_item.image_url,
            is_available=menu_item.is_available,
            is_promotion=menu_item.is_promotion,
            promo_price=menu_item.promo_price,
        )

        db.add(new_menu_item)
        db.commit()
        db.refresh(new_menu_item)

        return {
            "message": "Menu item created successfully",
            "menu_item": {
                "id": new_menu_item.id,
                "name_th": new_menu_item.name_th,
                "name_en": new_menu_item.name_en,
                "description_th": new_menu_item.description_th,
                "description_en": new_menu_item.description_en,
                "price": new_menu_item.price,
                "image_url": new_menu_item.image_url,
                "is_available": new_menu_item.is_available,
                "is_promotion": new_menu_item.is_promotion,
                "promo_price": new_menu_item.promo_price,
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.get("/menu-items")
def get_menu_items(db: Session = Depends(get_db)):
    items = db.query(MenuItem).order_by(MenuItem.id.asc()).all()

    return [
        {
            "id": item.id,
            "name_th": item.name_th,
            "name_en": item.name_en,
            "description_th": item.description_th,
            "description_en": item.description_en,
            "price": item.price,
            "image_url": item.image_url,
            "is_available": item.is_available,
            "is_promotion": item.is_promotion,
            "promo_price": item.promo_price,
        }
        for item in items
    ]    

@app.get("/menu/{qr_token}")
def get_menu_by_room(qr_token: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.qr_token == qr_token).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).all()

    return {
        "room": {
            "room_number": room.room_number,
            "floor": room.floor,
            "building": room.building,
        },
        "menu": [
            {
                "id": item.id,
                "name_th": item.name_th,
                "name_en": item.name_en,
                "price": item.price,
                "image_url": item.image_url,
                "is_promotion": item.is_promotion,
                "promo_price": item.promo_price,
            }
            for item in menu_items
        ],
    }

@app.post("/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.qr_token == order_data.qr_token).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order items cannot be empty")

    total_amount = 0

    new_order = Order(
        room_id=room.id,
        status="new",
        total_amount=0,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    created_items = []

    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()

        if not menu_item:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Menu item {item.menu_item_id} not found")

        if not menu_item.is_available:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Menu item {item.menu_item_id} is not available")

        unit_price = menu_item.promo_price if menu_item.is_promotion and menu_item.promo_price else menu_item.price
        line_total = unit_price * item.qty
        total_amount += line_total

        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=menu_item.id,
            qty=item.qty,
            unit_price=unit_price,
            line_total=line_total,
        )
        db.add(order_item)

        created_items.append(
            {
                "menu_item_id": menu_item.id,
                "name_th": menu_item.name_th,
                "qty": item.qty,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )

    new_order.total_amount = total_amount
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order created successfully",
        "order": {
            "order_id": new_order.id,
            "room_number": room.room_number,
            "status": new_order.status,
            "total_amount": new_order.total_amount,
            "items": created_items,
        },
    }

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    result = []

    for order in orders:
        room = db.query(Room).filter(Room.id == order.room_id).first()
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        items_data = []
        for order_item in order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.menu_item_id).first()

            items_data.append(
                {
                    "menu_item_id": order_item.menu_item_id,
                    "name_th": menu_item.name_th if menu_item else None,
                    "qty": order_item.qty,
                    "unit_price": order_item.unit_price,
                    "line_total": order_item.line_total,
                }
            )

        result.append(
            {
                "order_id": order.id,
                "room_number": room.room_number if room else None,
                "status": order.status,
                "total_amount": order.total_amount,
                "created_at": order.created_at,
                "items": items_data,
            }
        )

    return result

@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed_statuses = ["new", "accepted", "preparing", "ready", "delivered", "cancelled"]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    order.status = status_data.status
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "new_status": order.status,
    }

@app.get("/orders/new")
def get_new_orders(db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .filter(Order.status.in_(["new", "accepted", "preparing", "ready"]))
        .order_by(Order.id.desc())
        .all()
    )

    result = []

    for order in orders:
        room = db.query(Room).filter(Room.id == order.room_id).first()
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        items_data = []
        for order_item in order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.menu_item_id).first()

            items_data.append(
                {
                    "menu_item_id": order_item.menu_item_id,
                    "name_th": menu_item.name_th if menu_item else None,
                    "qty": order_item.qty,
                    "unit_price": order_item.unit_price,
                    "line_total": order_item.line_total,
                }
            )

        result.append(
            {
                "order_id": order.id,
                "room_number": room.room_number if room else None,
                "status": order.status,
                "total_amount": order.total_amount,
                "created_at": order.created_at,
                "items": items_data,
            }
        )

    return result

@app.get("/orders/{order_id}/ticket")
def get_order_ticket(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    room = db.query(Room).filter(Room.id == order.room_id).first()
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    lines = []
    lines.append("===== KITCHEN ORDER =====")
    lines.append(f"Order ID: {order.id}")
    lines.append(f"Room: {room.room_number if room else '-'}")
    lines.append(f"Time: {order.created_at}")
    lines.append("-------------------------")

    for item in order_items:
        menu = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()

        name = menu.name_th if menu else "Unknown"
        lines.append(f"{name} x{item.qty}")
        lines.append(f"  {item.unit_price} x {item.qty} = {item.line_total}")

    lines.append("-------------------------")
    lines.append(f"TOTAL: {order.total_amount}")
    lines.append("=========================")

    return {
        "ticket_text": "\n".join(lines)
    }

@app.get("/orders/{order_id}")
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    room = db.query(Room).filter(Room.id == order.room_id).first()
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    items_data = []
    for order_item in order_items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.menu_item_id).first()

        items_data.append(
            {
                "menu_item_id": order_item.menu_item_id,
                "name_th": menu_item.name_th if menu_item else None,
                "qty": order_item.qty,
                "unit_price": order_item.unit_price,
                "line_total": order_item.line_total,
            }
        )

    return {
        "order_id": order.id,
        "room_number": room.room_number if room else None,
        "status": order.status,
        "total_amount": order.total_amount,
        "created_at": order.created_at,
        "items": items_data,
    }
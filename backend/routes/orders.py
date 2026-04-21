from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Order, Pickup, Shipment
from schemas import OrderCreate, PickupCreate
from deps import get_db
from datetime import datetime, timedelta
from utils.deps import staff_only, admin_only

router = APIRouter(prefix="/orders", tags=["Orders"])


# 🧠 STATUS RULES (LOGIC)
def is_valid_transition(old, new):
    allowed = {
        "New": ["In Production", "Cancelled", "On Hold"],
        "In Production": ["Out for TryIn", "Complete", "On Hold"],
        "Out for TryIn": ["In Production", "On Hold"],
        "Complete": ["Delivered"],
        "Delivered": [],
        "On Hold": ["In Production"],
        "Cancelled": []
    }
    return new in allowed.get(old, [])


# 🔥 AUTO TRIGGERS (HELPERS)
def create_tryin_shipment(order, db):
    shipment = Shipment(order_id=order.id, client_id=order.client_id, type="tryin", status="shipped")
    db.add(shipment)

def create_final_shipment(order, db):
    shipment = Shipment(order_id=order.id, client_id=order.client_id, type="final", status="shipped")
    db.add(shipment)


# ➕ CREATE ORDER
@router.post("/", dependencies=[Depends(staff_only)])
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = Order(client_id=data.client_id, due_date=data.due_date, status="New", note=data.note)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


# 📄 GET ALL ORDERS
@router.get("/", dependencies=[Depends(staff_only)])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


# 🔄 SMART STATUS UPDATE (WORKFLOW)
@router.put("/{order_id}/status", dependencies=[Depends(staff_only)])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if not is_valid_transition(order.status, status):
        raise HTTPException(status_code=400, detail=f"Invalid transition {order.status} -> {status}")
    
    order.status = status
    if status == "Out for TryIn": create_tryin_shipment(order, db)
    if status == "Complete": create_final_shipment(order, db)
    db.commit()
    return {"msg": f"Status updated to {status}"}


# ❌ DELETE ORDER (ADMIN ONLY)
@router.delete("/{id}", dependencies=[Depends(admin_only)])
def delete_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order: raise HTTPException(status_code=404, detail="Not found")
    db.delete(order)
    db.commit()
    return {"msg": "Deleted"}


# ➕ PICKUP APIs
@router.post("/pickup", dependencies=[Depends(staff_only)])
def create_pickup(data: PickupCreate, db: Session = Depends(get_db)):
    pickup = Pickup(client_id=data.client_id, note=data.note)
    db.add(pickup)
    db.commit()
    return pickup

@router.get("/pickup", dependencies=[Depends(staff_only)])
def get_pickups(db: Session = Depends(get_db)):
    return db.query(Pickup).all()


# 🔥 1. OVERDUE ORDERS
@router.get("/overdue", dependencies=[Depends(staff_only)])
def get_overdue_orders(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    orders = db.query(Order).filter(Order.due_date < now, Order.status != "Delivered", Order.status != "Cancelled").all()
    for o in orders:
        if o.status != "Overdue": o.status = "Overdue"
    db.commit()
    return orders


# 🔥 2. SUMMARY
@router.get("/summary", dependencies=[Depends(staff_only)])
def order_summary(db: Session = Depends(get_db)):
    return {
        "new": db.query(Order).filter(Order.status == "New").count(),
        "production": db.query(Order).filter(Order.status == "In Production").count(),
        "complete": db.query(Order).filter(Order.status == "Complete").count(),
        "tryin": db.query(Order).filter(Order.status == "Out for TryIn").count(),
        "overdue": db.query(Order).filter(Order.status == "Overdue").count(),
        "hold": db.query(Order).filter(Order.status == "On Hold").count()
    }

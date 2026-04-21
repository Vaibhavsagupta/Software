from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String
from sqlalchemy.orm import Session
from models import Order, Pickup, Shipment
from schemas import OrderCreate, PickupCreate
from deps import get_db
from datetime import datetime, timedelta
from typing import Optional
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
def get_orders(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    search: Optional[str] = None,
    invoice_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    
    if invoice_status and invoice_status != "Ignore":
        query = query.join(Invoice).filter(Invoice.status == invoice_status)

    if status and status != "Ignore":
        query = query.filter(Order.status == status)
        
    if client_id:
        query = query.filter(Order.client_id == client_id)
        
    if search:
        query = query.filter(
            (Order.id.cast(String).contains(search)) |
            (Order.patient_name.contains(search)) |
            (Order.model_number.contains(search))
        )

    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
        
    return query.all()


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
    pickup = Pickup(
        client_id=data.client_id, 
        note=data.note,
        assigned_to=data.assigned_to,
        route=data.route,
        delivery_plan=data.delivery_plan,
        scheduled_date=data.scheduled_date
    )
    db.add(pickup)
    db.commit()
    db.refresh(pickup)
    return pickup

@router.get("/pickup", dependencies=[Depends(staff_only)])
def get_pickups(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    search: Optional[str] = None,
    assigned_to: Optional[str] = None,
    done_by: Optional[str] = None,
    route: Optional[str] = None,
    delivery_plan: Optional[str] = None,
    date_field: Optional[str] = "request_date", # request_date, scheduled_date, picked_up_date
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    order_created: Optional[str] = "Ignore",
    db: Session = Depends(get_db)
):
    query = db.query(Pickup)
    
    if status and status != "Ignore":
        query = query.filter(Pickup.status == status)
    
    if client_id:
        query = query.filter(Pickup.client_id == client_id)
        
    if search:
        query = query.filter(
            (Pickup.id.cast(String).contains(search)) | 
            (Pickup.note.contains(search))
        )

    if assigned_to and assigned_to != "Ignore":
        query = query.filter(Pickup.assigned_to == assigned_to)
        
    if done_by and done_by != "Ignore":
        query = query.filter(Pickup.done_by == done_by)
        
    if route and route != "Ignore":
        query = query.filter(Pickup.route == route)
        
    if delivery_plan and delivery_plan != "Ignore":
        query = query.filter(Pickup.delivery_plan == delivery_plan)
        
    if order_created == "Yes":
        query = query.filter(Pickup.status == "converted")
    elif order_created == "No":
        query = query.filter(Pickup.status != "converted")

    # Date Filtering
    col = Pickup.created_at
    if date_field == "scheduled_date": col = Pickup.scheduled_date
    elif date_field == "picked_up_date": col = Pickup.picked_up_date
    
    if start_date:
        query = query.filter(col >= start_date)
    if end_date:
        query = query.filter(col <= end_date)

    return query.all()


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

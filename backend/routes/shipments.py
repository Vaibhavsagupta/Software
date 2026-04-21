from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import String
from sqlalchemy.orm import Session
from models import Shipment, LogisticsPlan
from schemas import ShipmentCreate, ShipmentOut, LogisticsPlanOut
from typing import List
from deps import get_db
from datetime import datetime

router = APIRouter(prefix="/shipments", tags=["Shipments"])

# ➕ CREATE SHIPMENT (MAIN ENTRY)
@router.post("/")
def create_shipment(data: ShipmentCreate, db: Session = Depends(get_db)):
    shipment = Shipment(
        order_id=data.order_id,
        client_id=data.client_id,
        type=data.type,
        status="created"
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

# 🔥 SHIP TRYIN (STATUS = SHIPPED)
@router.post("/tryin")
def ship_tryin(data: ShipmentCreate, db: Session = Depends(get_db)):
    shipment = Shipment(
        order_id=data.order_id,
        client_id=data.client_id,
        type="tryin",
        status="shipped"
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

# 🔥 RETURN TRYIN
@router.put("/{shipment_id}/return")
def return_tryin(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(
        Shipment.id == shipment_id,
        Shipment.type == "tryin"
    ).first()
    if not shipment:
        return {"error": "TryIn not found"}
    shipment.status = "returned"
    db.commit()
    return {"msg": "TryIn Returned"}

# 🔥 SHIP FINAL PRODUCT
@router.post("/final")
def ship_final(data: ShipmentCreate, db: Session = Depends(get_db)):
    shipment = Shipment(
        order_id=data.order_id,
        client_id=data.client_id,
        type="final",
        status="shipped"
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

# 🔥 MARK DELIVERED
@router.put("/{shipment_id}/deliver")
def mark_delivered(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(
        Shipment.id == shipment_id,
        Shipment.type == "final"
    ).first()
    if not shipment:
        return {"error": "Shipment not found"}
    shipment.status = "delivered"
    db.commit()
    return {"msg": "Delivered"}

# 🔥 COMBINED FILTER API
@router.get("/filter", response_model=List[ShipmentOut])
def filter_shipments(
    type: str = None,
    status: str = None,
    client_id: int = None,
    start_date: str = None,
    end_date: str = None,
    search: str = None,
    today: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Shipment)
    if search:
        from ..models import Client, Order
        query = query.join(Client).join(Order).filter(
            (Shipment.id.cast(String).contains(search)) |
            (Client.name.contains(search)) |
            (Order.patient_name.contains(search))
        )
    if type:
        query = query.filter(Shipment.type == type)
    if status:
        query = query.filter(Shipment.status == status)
    if client_id:
        query = query.filter(Shipment.client_id == client_id)
    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            query = query.filter(Shipment.shipment_date >= sd)
        except: pass
    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            query = query.filter(Shipment.shipment_date <= ed)
        except: pass
    if today:
        today_date = datetime.utcnow().date()
        query = query.filter(Shipment.shipment_date >= today_date)
    return query.all()

# 🔥 SUMMARY API (DASHBOARD TYPE)
@router.get("/summary")
def shipment_summary(db: Session = Depends(get_db)):
    tryin_total = db.query(Shipment).filter(Shipment.type == "tryin").count()
    tryin_out = db.query(Shipment).filter(
        Shipment.type == "tryin",
        Shipment.status != "returned"
    ).count()
    final_total = db.query(Shipment).filter(Shipment.type == "final").count()
    final_delivered = db.query(Shipment).filter(
        Shipment.type == "final",
        Shipment.status == "delivered"
    ).count()
    return {
        "tryin": {"total": tryin_total, "out": tryin_out},
        "final": {"total": final_total, "delivered": final_delivered}
    }

# 🔥 BULK GENERATE SHIPMENT NOTES
@router.post("/bulk-generate")
def bulk_generate(order_ids: List[int], db: Session = Depends(get_db)):
    from ..models import Order
    created_count = 0
    for oid in order_ids:
        order = db.query(Order).filter(Order.id == oid).first()
        if order:
            exists = db.query(Shipment).filter(Shipment.order_id == oid).first()
            if not exists:
                shipment = Shipment(
                    order_id=order.id,
                    client_id=order.client_id,
                    type="final",
                    status="shipped"
                )
                order.status = "Complete"
                db.add(shipment)
                created_count += 1
    db.commit()
    return {"msg": f"Generated {created_count} Shipment Notes"}

# 🔥 LOGISTICS PLAN ROUTES
@router.get("/logistics", response_model=List[LogisticsPlanOut])
def get_plans(db: Session = Depends(get_db)):
    return db.query(LogisticsPlan).all()

@router.post("/logistics")
def create_plan(title: str, note: str, db: Session = Depends(get_db)):
    plan = LogisticsPlan(title=title, note=note)
    db.add(plan)
    db.commit()
    return {"msg": "Plan Created"}

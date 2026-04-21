from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Pickup, Order, Client
from schemas import PickupCreate
from deps import get_db

router = APIRouter(prefix="/pickups", tags=["Pickups"])


# CREATE PICKUP REQUEST
@router.post("/")
def create_pickup(pickup: PickupCreate, db: Session = Depends(get_db)):

    client = db.query(Client).filter(Client.id == pickup.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_pickup = Pickup(client_id=pickup.client_id)
    db.add(new_pickup)
    db.commit()
    db.refresh(new_pickup)

    return new_pickup


# GET ALL PICKUPS
@router.get("/")
def get_pickups(db: Session = Depends(get_db)):
    return db.query(Pickup).all()


# DO PICKUP (MARK PICKED)
@router.put("/{pickup_id}/pickup")
def do_pickup(pickup_id: int, db: Session = Depends(get_db)):

    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")

    pickup.status = "picked"
    db.commit()

    return {"msg": "Pickup completed"}


# CREATE ORDER FROM PICKUP
@router.post("/{pickup_id}/create-order")
def create_order_from_pickup(pickup_id: int, db: Session = Depends(get_db)):

    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")

    order = Order(
        client_id=pickup.client_id,
        status="New"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

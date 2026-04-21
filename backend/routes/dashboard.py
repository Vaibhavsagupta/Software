from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Client, Order, Shipment, Invoice, Payment, Expense
from deps import get_db
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# 📊 LAB PERFORMANCE TODAY
@router.get("/performance")
def lab_performance(db: Session = Depends(get_db)):

    today = datetime.utcnow().date()

    # 📅 FILTER TODAY DATA
    new_clients = db.query(Client).filter(Client.created_at >= today).count()
    new_orders = db.query(Order).filter(Order.created_at >= today).count()

    # 📦 TRYIN DISPATCHED (today)
    tryin_dispatched = db.query(Shipment).filter(
        Shipment.type == "tryin",
        Shipment.shipment_date >= today
    ).count()

    # 🔁 TRYIN RETURNED
    tryin_returned = db.query(Shipment).filter(
        Shipment.type == "tryin",
        Shipment.status == "returned"
    ).count()

    # 🚚 FINAL DELIVERIES
    final_deliveries = db.query(Shipment).filter(
        Shipment.type == "final",
        Shipment.status == "delivered"
    ).count()

    # 💰 INVOICES (today)
    invoices = db.query(Invoice).filter(Invoice.created_at >= today).all()
    invoiced_amount = sum(i.amount for i in invoices)

    # 💵 COLLECTION (today)
    payments = db.query(Payment).filter(Payment.date >= today).all()
    collection = sum(p.amount for p in payments)

    # 💸 EXPENSES (today)
    expense_list = db.query(Expense).filter(
        Expense.created_at >= today
    ).all()

    expenses = sum(e.amount for e in expense_list)

    # 💰 PROFIT
    profit = collection - expenses

    return {
        "new_clients": new_clients,
        "new_orders": new_orders,
        "tryin_dispatched": tryin_dispatched,
        "tryin_returned": tryin_returned,
        "final_deliveries": final_deliveries,
        "invoiced_amount": invoiced_amount,
        "collection": collection,
        "expenses": expenses,
        "profit_loss": profit
    }


# 🔄 WORKFLOW SUMMARY (ADVANCED)
@router.get("/workflow")
def workflow_summary(db: Session = Depends(get_db)):

    today = datetime.utcnow().date()

    # 🧮 BASIC STATUS COUNTS
    new = db.query(Order).filter(Order.status == "New").count()

    in_production = db.query(Order).filter(
        Order.status == "In Production"
    ).count()

    complete = db.query(Order).filter(
        Order.status == "Complete"
    ).count()

    hold = db.query(Order).filter(
        Order.status == "On Hold"
    ).count()

    try_in = db.query(Order).filter(
        Order.status == "Try In"
    ).count()

    # 🔥 OVERDUE LOGIC (IMPORTANT)
    overdue_orders = db.query(Order).filter(
        Order.due_date != None,
        Order.due_date < today,
        Order.status != "Delivered"
    ).all()

    overdue_count = len(overdue_orders)

    # 📅 OPTIONAL DETAIL (UI ke liye useful)
    overdue_list = [
        {
            "order_id": o.id,
            "client_id": o.client_id,
            "due_date": str(o.due_date)
        }
        for o in overdue_orders
    ]

    return {
        "new": new,
        "in_production": in_production,
        "complete": complete,
        "on_hold": hold,
        "try_in": try_in,
        "overdue": overdue_count,
        "overdue_list": overdue_list
    }


# 🚨 ALERT SYSTEM (INTELLIGENT)
@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):

    today = datetime.utcnow().date()

    # 📦 1. PENDING TRYINS (shipment created but not returned)
    pending_tryins = db.query(Shipment).filter(
        Shipment.type == "tryin",
        Shipment.status != "returned"
    ).all()

    pending_tryins_count = len(pending_tryins)

    pending_tryins_list = [
        {
            "shipment_id": s.id,
            "order_id": s.order_id
        }
        for s in pending_tryins
    ]


    # ⛔ 2. ON HOLD ORDERS
    on_hold_orders = db.query(Order).filter(
        Order.status == "On Hold"
    ).all()

    on_hold_count = len(on_hold_orders)

    on_hold_list = [
        {
            "order_id": o.id,
            "client_id": o.client_id
        }
        for o in on_hold_orders
    ]


    # 💰 3. PENDING BILLS (unpaid invoices)
    pending_bills = db.query(Invoice).filter(
        Invoice.status == "awaiting"
    ).all()

    pending_bills_count = len(pending_bills)

    pending_bills_list = [
        {
            "invoice_id": i.id,
            "amount": i.amount
        }
        for i in pending_bills
    ]


    # 🔴 4. OVERDUE ORDERS
    overdue_orders = db.query(Order).filter(
        Order.due_date != None,
        Order.due_date < today,
        Order.status != "Delivered"
    ).all()

    overdue_count = len(overdue_orders)

    overdue_list = [
        {
            "order_id": o.id,
            "due_date": str(o.due_date)
        }
        for o in overdue_orders
    ]


    return {
        "pending_tryins": {
            "count": pending_tryins_count,
            "data": pending_tryins_list
        },
        "on_hold": {
            "count": on_hold_count,
            "data": on_hold_list
        },
        "pending_bills": {
            "count": pending_bills_count,
            "data": pending_bills_list
        },
        "overdue_orders": {
            "count": overdue_count,
            "data": overdue_list
        }
    }

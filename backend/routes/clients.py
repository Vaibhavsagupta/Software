from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Client, Order, Shipment, Invoice, Payment, Message, Document, Task
from schemas import ClientCreate, MessageCreate, DocumentCreate, TaskCreate
from deps import get_db

router = APIRouter(prefix="/clients", tags=["Clients"])


# CREATE CLIENT
@router.post("/")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    new_client = Client(
        name=client.name,
        phone=client.phone,
        office_phone=client.office_phone,
        cell_phone=client.cell_phone,
        city=client.city,
        email=client.email
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


# QUICK / ADVANCED SEARCH
@router.get("/search")
def search_clients(query: str, field: str = "all", db: Session = Depends(get_db)):
    if field == "all":
        results = db.query(Client).filter(
            Client.name.ilike(f"%{query}%") |
            Client.phone.ilike(f"%{query}%") |
            Client.city.ilike(f"%{query}%") |
            Client.email.ilike(f"%{query}%")
        ).all()
    else:
        # Field specific search
        column = getattr(Client, field, Client.name)
        results = db.query(Client).filter(column.ilike(f"%{query}%")).all()
        
    return results


# GET ALL CLIENTS
@router.get("/")
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()


# GET SINGLE CLIENT
@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    return db.query(Client).filter(Client.id == client_id).first()


# UPDATE CLIENT
@router.put("/{client_id}")
def update_client(client_id: int, data: ClientCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        return {"error": "Client not found"}

    client.name = data.name
    client.phone = data.phone
    client.office_phone = data.office_phone
    client.cell_phone = data.cell_phone
    client.city = data.city
    client.email = data.email

    db.commit()
    return {"msg": "Client updated"}


# DELETE CLIENT
@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        return {"error": "Client not found"}

    db.delete(client)
    db.commit()
    return {"msg": "Client deleted"}


# 🔥 FULL PROFILE API
@router.get("/{client_id}/full")
def get_client_full(client_id: int, db: Session = Depends(get_db)):

    # 👤 CLIENT
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        return {"error": "Client not found"}


    # 📦 ORDERS
    orders = db.query(Order).filter(
        Order.client_id == client_id
    ).all()

    orders_data = [
        {
            "id": o.id,
            "status": o.status,
            "due_date": str(o.due_date)
        }
        for o in orders
    ]


    # 🚚 SHIPMENTS
    shipments = db.query(Shipment).filter(
        Shipment.client_id == client_id
    ).all()

    shipments_data = [
        {
            "id": s.id,
            "order_id": s.order_id,
            "type": s.type,
            "status": s.status
        }
        for s in shipments
    ]


    # 💰 INVOICES
    invoices = db.query(Invoice).filter(
        Invoice.client_id == client_id
    ).all()

    invoices_data = [
        {
            "id": i.id,
            "amount": i.amount,
            "paid": i.paid_amount,
            "status": i.status
        }
        for i in invoices
    ]


    # 💵 PAYMENTS
    payments = db.query(Payment).join(
        Invoice, Payment.invoice_id == Invoice.id
    ).filter(
        Invoice.client_id == client_id
    ).all()

    payments_data = [
        {
            "id": p.id,
            "invoice_id": p.invoice_id,
            "amount": p.amount
        }
        for p in payments
    ]


    # 💬 MESSAGES
    messages = db.query(Message).filter(Message.client_id == client_id).all()
    messages_data = [
        {"content": m.content, "direction": m.direction, "timestamp": str(m.timestamp)}
        for m in messages
    ]

    # 📂 DOCUMENTS
    documents = db.query(Document).filter(Document.client_id == client_id).all()
    documents_data = [
        {"filename": m.filename, "file_type": m.file_type, "upload_date": str(m.upload_date)}
        for m in documents
    ]

    # ✅ TASKS
    tasks = db.query(Task).filter(Task.client_id == client_id).all()
    tasks_data = [
        {"id": m.id, "title": m.title, "status": m.status, "due": str(m.due_date)}
        for m in tasks
    ]

    return {
        "client": {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "office_phone": client.office_phone,
            "cell_phone": client.cell_phone,
            "city": client.city,
            "email": client.email
        },
        "orders": orders_data,
        "shipments": shipments_data,
        "invoices": invoices_data,
        "payments": payments_data,
        "messages": messages_data,
        "documents": documents_data,
        "tasks": tasks_data
    }


# 🔥 CLIENT ANALYTICS API
@router.get("/{client_id}/analytics")
def client_analytics(client_id: int, db: Session = Depends(get_db)):

    # 📦 ORDERS
    orders = db.query(Order).filter(Order.client_id == client_id).all()

    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.status == "Complete"])
    pending_orders = total_orders - completed_orders


    # 🚚 SHIPMENTS
    shipments = db.query(Shipment).filter(
        Shipment.client_id == client_id
    ).all()

    tryin_count = len([s for s in shipments if s.type == "tryin"])
    final_count = len([s for s in shipments if s.type == "final"])


    # 💰 INVOICES
    invoices = db.query(Invoice).filter(
        Invoice.client_id == client_id
    ).all()

    total_business = sum(i.amount for i in invoices)
    total_paid = sum(i.paid_amount for i in invoices)

    pending_amount = total_business - total_paid


    return {
        "orders": {
            "total": total_orders,
            "completed": completed_orders,
            "pending": pending_orders
        },
        "shipments": {
            "tryin": tryin_count,
            "final": final_count
        },
        "finance": {
            "total_business": total_business,
            "total_paid": total_paid,
            "pending": pending_amount
        }
    }


# 📦 ORDERS FILTER BY STATUS
@router.get("/{client_id}/orders")
def get_client_orders(client_id: int, status: str = None, db: Session = Depends(get_db)):

    query = db.query(Order).filter(Order.client_id == client_id)

    if status:
        query = query.filter(Order.status == status)

    orders = query.all()

    return [
        {
            "id": o.id,
            "status": o.status,
            "due_date": str(o.due_date)
        }
        for o in orders
    ]


# 💰 INVOICE FILTER (Updated for Financials)
@router.get("/{client_id}/invoices")
def get_client_invoices(client_id: int, status: str = None, db: Session = Depends(get_db)):

    query = db.query(Invoice).filter(Invoice.client_id == client_id)

    if status:
        query = query.filter(Invoice.status == status)

    invoices = query.all()

    return [
        {
            "id": i.id,
            "amount": i.amount,
            "paid": i.paid_amount,
            "status": i.status,
            "due": i.amount - i.paid_amount
        }
        for i in invoices
    ]


# 🔥 CLIENT PAYMENTS API
@router.get("/{client_id}/payments")
def client_payments(client_id: int, db: Session = Depends(get_db)):

    payments = db.query(Payment).join(
        Invoice, Payment.invoice_id == Invoice.id
    ).filter(
        Invoice.client_id == client_id
    ).all()

    return [
        {
            "payment_id": p.id,
            "invoice_id": p.invoice_id,
            "amount": p.amount,
            "date": str(p.date)
        }
        for p in payments
    ]


# 🔥 FINANCIAL SUMMARY API
@router.get("/{client_id}/financial-summary")
def financial_summary(client_id: int, db: Session = Depends(get_db)):

    invoices = db.query(Invoice).filter(
        Invoice.client_id == client_id
    ).all()

    total = sum(i.amount for i in invoices)
    paid = sum(i.paid_amount for i in invoices)

    pending = total - paid

    return {
        "total_business": total,
        "total_paid": paid,
        "pending": pending
    }

# 💬 MESSAGES API
@router.post("/{client_id}/messages")
def add_message(client_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Message(
        client_id=client_id,
        content=message.content,
        direction=message.direction
    )
    db.add(new_msg)
    db.commit()
    return {"msg": "Message added"}

@router.get("/{client_id}/messages")
def get_messages(client_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.client_id == client_id).order_by(Message.timestamp.desc()).all()

# 📂 DOCUMENTS API
@router.post("/{client_id}/documents")
def add_document(client_id: int, document: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = Document(
        client_id=client_id,
        filename=document.filename,
        file_type=document.file_type
    )
    db.add(new_doc)
    db.commit()
    return {"msg": "Document logged"}

@router.get("/{client_id}/documents")
def get_documents(client_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.client_id == client_id).all()

# ✅ TASKS API
@router.post("/{client_id}/tasks")
def add_task(client_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        client_id=client_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    return {"msg": "Task assigned"}

@router.get("/{client_id}/tasks")
def get_tasks(client_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.client_id == client_id).all()

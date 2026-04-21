from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from models import Invoice, Payment, Adjustment, Order, ProductCategory, ProductPrice
from schemas import InvoiceCreate, PaymentCreate, AdjustmentCreate, ProductCategoryOut, ProductPriceOut, InvoiceOut
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, cast
from deps import get_db

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# 🔄 AUTO UPDATE STATUS (HELPER)
def update_invoice_status(invoice):
    if invoice.paid_amount == 0:
        invoice.status = "awaiting"
    elif invoice.paid_amount < invoice.amount:
        invoice.status = "partial"
    else:
        invoice.status = "paid"

# 💰 INVOICE APIs

@router.post("/invoice")
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = Invoice(
        client_id=data.client_id,
        order_id=data.order_id,
        amount=data.amount,
        paid_amount=0,
        status="awaiting"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/invoice", response_model=List[InvoiceOut])
def get_invoices(db: Session = Depends(get_db)):
    # Joining with Client for detailed view
    return db.query(Invoice).options(joinedload(Invoice.client)).all()

@router.get("/pending-invoices")
def get_pending_invoices(
    client_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Orders that don't have an invoice yet
    query = db.query(Order).outerjoin(Invoice).filter(Invoice.id == None).options(joinedload(Order.client))
    
    if client_id:
        query = query.filter(Order.client_id == client_id)
    
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.created_at >= sd)
        except: pass
        
    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= ed)
        except: pass

    orders = query.order_by(Order.created_at.desc()).all()
    
    results = []
    for o in orders:
        shipment = o.shipments[0] if o.shipments else None
        results.append({
            "order_id": o.id,
            "order_date": o.created_at,
            "client_id": o.client_id,
            "client_name": o.client.name if o.client else "Unknown",
            "patient_name": o.patient_name or "",
            "products": o.products or "",
            "model_number": o.model_number or "",
            "shipment_number": shipment.id if shipment else "",
            "shipment_date": shipment.shipment_date if shipment else "",
            "order_amount": o.order_amount or 0.0,
            "status": o.status
        })
    return results

@router.get("/invoice/status/{status}", response_model=List[InvoiceOut])
def get_invoice_by_status(status: str, db: Session = Depends(get_db)):
    return db.query(Invoice).filter(Invoice.status == status).options(joinedload(Invoice.client)).all()

@router.get("/search", response_model=List[InvoiceOut])
def search_invoices(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Invoice).options(joinedload(Invoice.client))
    
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    
    if status and status.lower() != "ignore":
        query = query.filter(Invoice.status == status.lower())
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Invoice.created_at >= start_dt)
        except: pass
        
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Invoice.created_at <= end_dt)
        except: pass

    if search:
        # Search by Invoice ID or Client Name
        search_filter = cast(Invoice.id, String).contains(search)
        query = query.filter(search_filter)
        
    return query.order_by(Invoice.created_at.desc()).all()

@router.put("/invoice/{id}/cancel")
def cancel_invoice(id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Not found")
    invoice.status = "cancelled"
    db.commit()
    return {"msg": "Cancelled"}

# 💵 PAYMENT APIs (COLLECTION SYSTEM)

@router.post("/payment")
def add_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == data.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    payment = Payment(
        invoice_id=data.invoice_id,
        amount=data.amount,
        client_id=data.client_id,
        method=data.method,
        note=data.note
    )
    db.add(payment)

    invoice.paid_amount += data.amount
    update_invoice_status(invoice)

    db.commit()
    return {"msg": "Payment added"}

@router.get("/payment")
def get_payments(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Payment).options(joinedload(Payment.client))
    
    if client_id:
        query = query.filter(Payment.client_id == client_id)
        
    if status and status.lower() != "ignore":
        query = query.filter(Payment.status == status.lower())
    elif not status:
         query = query.filter(Payment.status == "active")
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Payment.date >= start_dt)
        except: pass
        
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Payment.date <= end_dt)
        except: pass
        
    return query.order_by(Payment.date.desc()).all()

# ⚖️ ADJUSTMENTS APIs

@router.post("/adjustment")
def create_adjustment(data: AdjustmentCreate, db: Session = Depends(get_db)):
    adj = Adjustment(
        client_id=data.client_id,
        type=data.type,
        amount=data.amount,
        note=data.note
    )
    db.add(adj)
    db.commit()
    return {"msg": "Adjustment added"}

@router.get("/adjustment")
def get_adjustments(
    type: Optional[str] = None,
    client_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Adjustment).options(joinedload(Adjustment.client))
    
    if type:
        query = query.filter(Adjustment.type == type.lower())
        
    if client_id:
        query = query.filter(Adjustment.client_id == client_id)
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Adjustment.date >= start_dt)
        except: pass
        
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Adjustment.date <= end_dt)
        except: pass
        
    return query.order_by(Adjustment.date.desc()).all()

# 🔥 FINANCIAL SUMMARY
@router.get("/summary")
def financial_summary(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    total_business = sum(i.amount for i in invoices)
    total_paid = sum(i.paid_amount for i in invoices)
    pending = total_business - total_paid

    adjustments = db.query(Adjustment).all()
    total_credit = sum(a.amount for a in adjustments if a.type == "credit")
    total_debit = sum(a.amount for a in adjustments if a.type == "debit")

    final_pending = pending - total_credit + total_debit

    return {
        "total_business": total_business,
        "total_paid": total_paid,
        "pending_before_adjustment": pending,
        "credit": total_credit,
        "debit": total_debit,
        "final_pending": final_pending
    }

# 📦 PRICE LIST APIs
@router.get("/product-categories", response_model=List[ProductCategoryOut])
def get_product_categories(db: Session = Depends(get_db)):
    return db.query(ProductCategory).all()

@router.get("/price-list/{category_id}", response_model=List[ProductPriceOut])
def get_price_list(category_id: int, db: Session = Depends(get_db)):
    return db.query(ProductPrice).filter(ProductPrice.category_id == category_id).all()

@router.put("/price-list/update")
def update_prices(prices: List[ProductPriceOut], db: Session = Depends(get_db)):
    for p in prices:
        db_price = db.query(ProductPrice).filter(ProductPrice.id == p.id).first()
        if db_price:
            db_price.charge = p.charge
            db_price.code = p.code
    db.commit()
    return {"msg": "Prices updated successfully"}

@router.post("/generate-bulk-invoices")
def generate_bulk_invoices(order_ids: List[int], db: Session = Depends(get_db)):
    created_count = 0
    for oid in order_ids:
        order = db.query(Order).filter(Order.id == oid).first()
        if order and not order.invoice:
            invoice = Invoice(
                client_id=order.client_id,
                order_id=order.id,
                amount=order.order_amount or 0.0,
                paid_amount=0,
                status="awaiting"
            )
            db.add(invoice)
            created_count += 1
    db.commit()
    return {"msg": f"Generated {created_count} invoices"}

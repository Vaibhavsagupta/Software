from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import datetime, timedelta

def seed():
    db = SessionLocal()
    
    # 1. Ensure we have a client
    client = db.query(models.Client).first()
    if not client:
        client = models.Client(
            name="SOHAR DENTAL CLINIC",
            phone="96812345678",
            city="Sohar",
            email="info@sohardental.com"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
    
    # 2. Add some orders that are ready to be invoiced (no invoice linked)
    orders_data = [
        {
            "patient_name": "ABDULLAH",
            "products": "ZIRCON - 0",
            "model_number": "19758",
            "order_amount": 120.0,
            "status": "Complete",
            "note": "Standard case"
        },
        {
            "patient_name": "RUQUIYA",
            "products": "BITE RIM U/L - 1",
            "model_number": "19757",
            "order_amount": 45.0,
            "status": "Complete",
            "note": "Urgent"
        },
        {
            "patient_name": "SALAJA SUNTI",
            "products": "PFM - 1",
            "model_number": "19753",
            "order_amount": 80.0,
            "status": "Complete",
            "note": "Wait for shade"
        },
        {
            "patient_name": "KHAMIS AL FAHDI",
            "products": "VENEER - 0",
            "model_number": "19751",
            "order_amount": 250.0,
            "status": "In Production",
            "note": "Match natural color"
        }
    ]
    
    for o_data in orders_data:
        order = models.Order(
            client_id=client.id,
            patient_name=o_data["patient_name"],
            products=o_data["products"],
            model_number=o_data["model_number"],
            order_amount=o_data["order_amount"],
            status=o_data["status"],
            note=o_data["note"],
            due_date=datetime.utcnow() + timedelta(days=3)
        )
        db.add(order)
    
    db.commit()
    
    # 3. Create some Invoices in 'awaiting' status
    complete_orders = db.query(models.Order).filter(models.Order.status == "Complete").all()
    for o in complete_orders[:2]: # Only invoice the first two for demonstration
        invoice = models.Invoice(
            client_id=o.client_id,
            order_id=o.id,
            amount=o.order_amount,
            paid_amount=0,
            status="awaiting",
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invoice)
        
    # 4. Create some Invoices in 'paid' status
    for o in complete_orders[2:4]: # Invoice the next two as paid
        invoice = models.Invoice(
            client_id=o.client_id,
            order_id=o.id,
            amount=o.order_amount,
            paid_amount=o.order_amount, # Fully paid
            status="paid",
            due_date=datetime.utcnow() - timedelta(days=2) # Already due
        )
        db.add(invoice)
        
    # 5. Create some Invoices in 'cancelled' status
    for o in complete_orders[4:6]: # Invoice the next two as cancelled
        if not o: continue
        invoice = models.Invoice(
            client_id=o.client_id,
            order_id=o.id,
            amount=o.order_amount,
            paid_amount=0,
            status="cancelled",
            due_date=datetime.utcnow() - timedelta(days=5)
        )
        db.add(invoice)
        
    # 6. Create some Payments (Receipts)
    paid_invoices = db.query(models.Invoice).filter(models.Invoice.status == "paid").all()
    for pi in paid_invoices:
        payment = models.Payment(
            client_id=pi.client_id,
            invoice_id=pi.id,
            amount=pi.amount + 5, # Paying a bit extra for credit demo
            applied_amount=pi.amount,
            method="Bank Transfer",
            note="Full payment plus surplus",
            date=datetime.utcnow() - timedelta(days=1)
        )
        db.add(payment)
        
    db.commit()
    
    # 7. Create some Cancelled Payments
    for pi in paid_invoices[:1]: # Cancel the first one's payment equivalent
        cancelled_payment = models.Payment(
            client_id=pi.client_id,
            invoice_id=None,
            amount=500.0,
            applied_amount=0,
            method="Cash",
            status="cancelled",
            note="Payment bounced / Error",
            date=datetime.utcnow() - timedelta(days=3)
        )
        db.add(cancelled_payment)
        
    # 8. Create some Credit Adjustments
    active_client = db.query(models.Client).first()
    paid_invoice = db.query(models.Invoice).filter(models.Invoice.status == "paid").first()
    if active_client:
        adjustment = models.Adjustment(
            client_id=active_client.id,
            type="credit",
            adj_type="Discount",
            amount=50.0,
            note="Loyalty discount applied",
            applied_to_invoice_id=paid_invoice.id if paid_invoice else None,
            date=datetime.utcnow() - timedelta(days=2)
        )
        db.add(adjustment)
        
    # 9. Create some Debit Adjustments
    if active_client:
        adjustment = models.Adjustment(
            client_id=active_client.id,
            type="debit",
            adj_type="Correction",
            amount=120.0,
            note="Price correction for previous order",
            applied_to_invoice_id=None,
            date=datetime.utcnow() - timedelta(days=1)
        )
        db.add(adjustment)
        
    # 10. Create some Journal Vouchers
    if active_client:
        adjustment = models.Adjustment(
            client_id=active_client.id,
            type="journal",
            adj_type="General Adjustment",
            amount=-250.0, # Credit adjustment via JV
            note="Year-end reconciliation",
            applied_to_invoice_id=None,
            date=datetime.utcnow() - timedelta(days=5)
        )
        db.add(adjustment)
        
    db.commit()
    print("Sample orders, invoices, payments, and all adjustments including JV seeded successfully!")

if __name__ == "__main__":
    seed()

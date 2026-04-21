from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Client, Order, Pickup, Shipment, Invoice, Payment, Adjustment, ProductCategory, ProductPrice, Expense, Message, Task
from datetime import datetime, timedelta
import random

# Recreate tables (optional, but ensures clean start for demo)
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_demo():
    print("Clearing old data...")
    db.query(Task).delete()
    db.query(Message).delete()
    db.query(Expense).delete()
    db.query(ProductPrice).delete()
    db.query(ProductCategory).delete()
    db.query(Adjustment).delete()
    db.query(Payment).delete()
    db.query(Invoice).delete()
    db.query(Shipment).delete()
    db.query(Pickup).delete()
    db.query(Order).delete()
    db.query(Client).delete()
    db.commit()

    print("Adding Demo Clients...")
    clients = [
        Client(name="Dr. Sharma Dental Clinic", city="New Delhi", email="sharma@example.com", phone="9876543210"),
        Client(name="Smile Perfect Orthodontics", city="Mumbai", email="smile@example.com", phone="9876543211"),
        Client(name="City Dental Care", city="Bangalore", email="city@example.com", phone="9876543212"),
        Client(name="Advanced Tooth Lab", city="Hyderabad", email="advanced@example.com", phone="9876543213"),
        Client(name="Global Dental Hub", city="Pune", email="global@example.com", phone="9876543214")
    ]
    db.add_all(clients)
    db.commit()

    print("Adding Product Categories & Prices...")
    cat1 = ProductCategory(name="Crown & Bridge")
    cat2 = ProductCategory(name="Dentures")
    db.add_all([cat1, cat2])
    db.commit()

    prices = [
        ProductPrice(category_id=cat1.id, name="PFM Standard", code="CB01", charge=1200.0),
        ProductPrice(category_id=cat1.id, name="Zirconia Premium", code="CB02", charge=3500.0),
        ProductPrice(category_id=cat2.id, name="Partial Acrylic", code="DT01", charge=800.0),
        ProductPrice(category_id=cat2.id, name="Full Denture Upper", code="DT02", charge=2500.0)
    ]
    db.add_all(prices)
    db.commit()

    print("Adding Realistic Orders...")
    now = datetime.utcnow()
    orders = [
        # Client 1: Active Production
        Order(client_id=clients[0].id, patient_name="Amit Kumar", products="Zirconia Premium (3 units)", status="In Production", order_amount=10500.0, due_date=now + timedelta(days=3), note="Shade A2, Upper right"),
        Order(client_id=clients[0].id, patient_name="Sunita Devi", products="PFM Standard", status="New", order_amount=1200.0, due_date=now + timedelta(days=5)),
        
        # Client 2: Try-In and Complete
        Order(client_id=clients[1].id, patient_name="John Doe", products="Metal Ceramic Crown", status="Out for TryIn", order_amount=2400.0, due_date=now + timedelta(days=2)),
        Order(client_id=clients[1].id, patient_name="Jane Smith", products="Flexible Denture", status="Complete", order_amount=4500.0, due_date=now - timedelta(days=1)),
        
        # Client 3: Delivered and Repeat/Repair
        Order(client_id=clients[2].id, patient_name="Rajesh Iyer", products="Bridge 4 units", status="Delivered", order_amount=4800.0, due_date=now - timedelta(days=5)),
        Order(client_id=clients[2].id, patient_name="Priya Singh", products="Repair: Fractured Crown", status="Repeat/Repair", order_amount=500.0, due_date=now + timedelta(days=1), note="Patient reported fracture after 2 days"),
        
        # Client 4: Overdue and Hold
        Order(client_id=clients[3].id, patient_name="Vikram Rathore", products="Implant Abutment", status="Overdue", order_amount=6000.0, due_date=now - timedelta(days=3)),
        Order(client_id=clients[3].id, patient_name="Neha Gupta", products="Custom Tray", status="On Hold", order_amount=300.0, due_date=now + timedelta(days=10), note="Waiting for clear impression"),
        
        # Client 5: Cancelled
        Order(client_id=clients[4].id, patient_name="Sameer Khan", products="Full Denture Set", status="Cancelled", order_amount=5000.0, due_date=now, note="Client changed mind")
    ]
    db.add_all(orders)
    db.commit()

    print("Adding Pickups...")
    pickups = [
        Pickup(client_id=clients[0].id, note="Collect 2 new impressions", status="pending"),
        Pickup(client_id=clients[1].id, note="Return 1 shade guide", status="completed"),
        Pickup(client_id=clients[2].id, note="Pickup urgently", status="converted")
    ]
    db.add_all(pickups)
    db.commit()

    print("Adding Shipments...")
    shipments = [
        Shipment(order_id=orders[2].id, client_id=clients[1].id, type="tryin", status="shipped"),
        Shipment(order_id=orders[3].id, client_id=clients[1].id, type="final", status="shipped")
    ]
    db.add_all(shipments)
    db.commit()

    print("Adding Financial Data (Invoices & Payments)...")
    # Invoice for Completed order
    inv1 = Invoice(order_id=orders[3].id, client_id=clients[1].id, amount=4500.0, status="awaiting", due_date=now + timedelta(days=7))
    # Invoice for Delivered order
    inv2 = Invoice(order_id=orders[4].id, client_id=clients[2].id, amount=4800.0, status="paid", due_date=now - timedelta(days=2))
    db.add_all([inv1, inv2])
    db.commit()

    # Payment for Paid invoice
    pay1 = Payment(client_id=clients[2].id, invoice_id=inv2.id, amount=4800.0, applied_amount=4800.0, method="Bank Transfer", note="Full Payment Order #5")
    # Partial payment for awaiting invoice
    pay2 = Payment(client_id=clients[1].id, invoice_id=inv1.id, amount=2000.0, applied_amount=2000.0, method="Cash", note="Token amount")
    db.add_all([pay1, pay2])
    db.commit()

    # Update invoice paid status
    inv2.paid_amount = 4800.0
    inv1.paid_amount = 2000.0
    db.commit()

    print("Adding Adjustments...")
    adj1 = Adjustment(client_id=clients[0].id, type="credit", amount=500.0, note="Bulk discount for March")
    adj2 = Adjustment(client_id=clients[1].id, type="debit", amount=100.0, note="Late courier charge")
    db.add_all([adj1, adj2])
    db.commit()

    print("Adding Expenses...")
    expenses = [
        Expense(title="Lab Ceramic Powder", amount=12000.0),
        Expense(title="Electricity Bill", amount=4500.0),
        Expense(title="Courier Charges", amount=1800.0)
    ]
    db.add_all(expenses)
    db.commit()

    print("Adding CRM Data (Messages & Tasks)...")
    messages = [
        Message(client_id=clients[0].id, content="Order #1 will be ready by tomorrow.", direction="outbound"),
        Message(client_id=clients[0].id, content="Thank you, please ensure shade matches A2.", direction="inbound")
    ]
    tasks = [
        Task(client_id=clients[1].id, title="Follow up on Try-In", description="Ask Dr. for fit feedback"),
        Task(client_id=clients[2].id, title="Confirm bank transfer", status="done")
    ]
    db.add_all(messages + tasks)
    db.commit()

    print("\n✅ Demo Data Seeded Successfully!")

if __name__ == "__main__":
    seed_demo()
    db.close()

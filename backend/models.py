from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# 👤 USER AUTH
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="staff")  # admin / staff

# 👤 CLIENT
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    office_phone = Column(String, nullable=True)
    cell_phone = Column(String, nullable=True)
    city = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="client")
    payments = relationship("Payment", back_populates="client")
    adjustments = relationship("Adjustment", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    messages = relationship("Message", back_populates="client")
    documents = relationship("Document", back_populates="client")
    tasks = relationship("Task", back_populates="client")

# 📦 ORDER
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    status = Column(String, default="New")
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    note = Column(String, nullable=True)
    
    # New fields for Dental Lab
    patient_name = Column(String, nullable=True)
    products = Column(String, nullable=True) # JSON or comma separated string
    model_number = Column(String, nullable=True)
    order_amount = Column(Float, default=0.0)
    
    client = relationship("Client", back_populates="orders")
    shipments = relationship("Shipment", back_populates="order")
    invoice = relationship("Invoice", uselist=False, back_populates="order")

# 🚚 PICKUP
class Pickup(Base):
    __tablename__ = "pickups"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    status = Column(String, default="pending")  # pending / completed / converted
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)
    
    # New Fields for Advanced Tracking
    assigned_to = Column(String, nullable=True)
    done_by = Column(String, nullable=True)
    route = Column(String, nullable=True)
    delivery_plan = Column(String, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    picked_up_date = Column(DateTime, nullable=True)

    client = relationship("Client")

# 🚚 SHIPMENT
class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    type = Column(String)   # "tryin" / "final"
    status = Column(String, default="created")  # created / shipped / returned / delivered
    shipment_date = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="shipments")
    client = relationship("Client")


# 💰 INVOICE
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))

    amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String, default="awaiting")  # awaiting / paid / cancelled
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="invoice")
    client = relationship("Client", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

# 💵 PAYMENT
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    amount = Column(Float, nullable=False)
    applied_amount = Column(Float, default=0.0) # How much was applied to invoices
    method = Column(String, default="Cash")  # Cash / Bank / Online
    status = Column(String, default="active") # active / cancelled
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)

    client = relationship("Client", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

# 🔄 ADJUSTMENTS
class Adjustment(Base):
    __tablename__ = "adjustments"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    type = Column(String)  # credit / debit / journal
    adj_type = Column(String, nullable=True) # Discount / Return / Correction
    amount = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    applied_to_invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="adjustments")

class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class ProductPrice(Base):
    __tablename__ = "product_prices"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    name = Column(String, index=True)
    code = Column(String, nullable=True)
    charge = Column(Float, default=0.0)

# 💸 EXPENSES
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 🚛 LOGISTICS PLAN
class LogisticsPlan(Base):
    __tablename__ = "logistics_plans"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    note = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

# 💬 MESSAGES
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    content = Column(String, nullable=False)
    direction = Column(String, default="outbound") # inbound / outbound
    timestamp = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="messages")

# 📂 DOCUMENTS
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    filename = Column(String, nullable=False)
    file_type = Column(String) # pdf, image, etc.
    upload_date = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="documents")

# ✅ TASKS
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending") # pending / done
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="tasks")

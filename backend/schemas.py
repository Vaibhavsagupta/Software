from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# -------- AUTH --------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "staff"

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

# -------- CLIENT --------
class ClientBase(BaseModel):
    name: str
    phone: Optional[str] = None
    office_phone: Optional[str] = None
    cell_phone: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProductPriceBase(BaseModel):
    category_id: int
    name: str
    code: Optional[str] = None
    charge: float = 0.0

class ProductPriceOut(ProductPriceBase):
    id: int
    class Config:
        from_attributes = True

class ProductCategoryOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

# -------- ORDER --------
class OrderBase(BaseModel):
    model_config = {"protected_namespaces": ()}
    client_id: int
    due_date: Optional[datetime] = None
    note: Optional[str] = None
    status: Optional[str] = "New"
    patient_name: Optional[str] = None
    products: Optional[str] = None
    model_number: Optional[str] = None
    order_amount: Optional[float] = 0.0
    warranty_expiry: Optional[datetime] = None

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    created_at: datetime
    client: Optional[ClientOut] = None
    class Config:
        from_attributes = True

# -------- SHIPMENT --------
class ShipmentBase(BaseModel):
    order_id: int
    client_id: int
    type: str  # tryin / final
    status: Optional[str] = "created"

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentOut(ShipmentBase):
    id: int
    shipment_date: datetime
    client: Optional[ClientOut] = None
    order: Optional[OrderOut] = None
    class Config:
        from_attributes = True

class LogisticsPlanOut(BaseModel):
    id: int
    title: str
    note: Optional[str] = None
    date: datetime
    class Config:
        from_attributes = True

# -------- ACCOUNTS --------
class InvoiceBase(BaseModel):
    order_id: int
    client_id: int
    amount: float
    paid_amount: Optional[float] = 0.0
    status: Optional[str] = "awaiting"
    due_date: Optional[datetime] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceOut(InvoiceBase):
    id: int
    created_at: datetime
    client: Optional[ClientOut] = None
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    invoice_id: Optional[int] = None
    client_id: int
    amount: float
    applied_amount: Optional[float] = 0.0
    method: Optional[str] = "Cash"
    status: Optional[str] = "active"
    note: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    date: datetime
    client: Optional[ClientOut] = None
    class Config:
        from_attributes = True

class AdjustmentBase(BaseModel):
    client_id: int
    type: str  # credit / debit / journal
    adj_type: Optional[str] = "Discount"
    amount: float
    note: Optional[str] = None
    applied_to_invoice_id: Optional[int] = None

class AdjustmentCreate(AdjustmentBase):
    pass

class AdjustmentOut(AdjustmentBase):
    id: int
    date: datetime
    client: Optional[ClientOut] = None
    class Config:
        from_attributes = True

# -------- PICKUP --------
class PickupCreate(BaseModel):
    client_id: int
    note: Optional[str] = None

class PickupOut(BaseModel):
    id: int
    client_id: int
    status: str
    created_at: datetime
    note: Optional[str] = None
    class Config:
        from_attributes = True

# -------- EXPENSES --------
class ExpenseCreate(BaseModel):
    title: str
    amount: float

class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: float
    created_at: datetime
    class Config:
        from_attributes = True

# -------- MESSAGES --------
class MessageCreate(BaseModel):
    client_id: int
    content: str
    direction: Optional[str] = "outbound"

class MessageOut(BaseModel):
    id: int
    client_id: int
    content: str
    direction: str
    timestamp: datetime
    class Config:
        from_attributes = True

# -------- DOCUMENTS --------
class DocumentCreate(BaseModel):
    client_id: int
    filename: str
    file_type: Optional[str] = None

class DocumentOut(BaseModel):
    id: int
    client_id: int
    filename: str
    file_type: str
    upload_date: datetime
    class Config:
        from_attributes = True

# -------- TASKS --------
class TaskCreate(BaseModel):
    client_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskOut(BaseModel):
    id: int
    client_id: int
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from routes import auth, clients, orders, pickups, shipments, accounts, dashboard, expenses

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ERP Backend")

# Enable CORS
origins = [
    "https://dental-chi-fawn.vercel.app",
    "http://localhost:4537",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(pickups.router)
app.include_router(shipments.router)
app.include_router(accounts.router)
app.include_router(dashboard.router)
app.include_router(expenses.router)






@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return ""

@app.get("/")
def home():
    return {"message": "ERP Running 🚀"}


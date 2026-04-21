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


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Include routes
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(pickups.router)
app.include_router(shipments.router)
app.include_router(accounts.router)
app.include_router(dashboard.router)
app.include_router(expenses.router)

# Serve Static Files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{full_path:path}")
def serve_all(full_path: str):
    file_path = os.path.join(frontend_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return ""

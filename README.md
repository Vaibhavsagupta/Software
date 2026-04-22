# 🦷 Dental ERP System

A complete, lightweight, and modular Enterprise Resource Planning (ERP) system designed for Dental Labs. This project features a robust FastAPI backend and a clean VanillaJS frontend.

## 🚀 Key Modules
- **🔐 Auth**: Secure User Registration & Login (JWT-based).
- **👥 Clients**: Client management and history.
- **📦 Orders**: Workflow tracking (New ➡️ In Production ➡️ Delivered).
- **🚚 Shipments**: Lifecycle management for TryIn and Final deliveries.
- **💰 Accounts**: Automated Invoicing, Payments, and Financial Adjustments.
- **📊 Dashboard**: Real-time Lab Performance, Workflow Summary, and Overdue Alerts.

---

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python), SQLAlchemy (ORM), SQLite (Database), Pydantic.
- **Frontend**: Vanilla JavaScript, HTML5, CSS3.
- **Auth**: JWT (JSON Web Tokens), Passlib (Bcrypt).

---

## 📁 Project Structure
```plaintext
/
├── backend/            # FastAPI Source Code
│   ├── routes/         # Modular API Endpoints
│   ├── main.py         # App Entry Point
│   ├── models.py       # Database Schema
│   ├── database.py     # SQLAlchemy Configuration
│   └── requirements.txt
└── frontend/           # Web Interface
    ├── index.html      # Dashboard
    ├── clients.html    # Client Management
    ├── js/api.js       # Core API Logic
    └── css/style.css   # Styling
```

---

## ⚡ Setup & Installation

### 1. Backend Setup
Make sure you have **Python 3.8+** installed.

1.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
2.  Run the server from the root:
    ```bash
    uvicorn main:app --reload --port 7070
    ```
    *The backend will be live at `http://127.0.0.1:7070`*

### 2. Frontend Setup
The frontend is built with vanilla technologies, so no installation is required!

1.  Simply open `frontend/index.html` in any modern web browser.
2.  Use the navigation bar at the top to switch between modules.

---

## 🧪 Testing the APIs
Once the backend is running, you can access the interactive Swagger documentation at:
👉 **[http://127.0.0.1:7070/docs](http://127.0.0.1:7070/docs)**

---

## 🔗 Business Flow Demo
1.  **Home**: View overall lab stats.
2.  **Clients**: Add a new Doctor/Clinic.
3.  **Orders**: Create an order for a client.
4.  **Shipments**: Dispatch a TryIn or Final product.
5.  **Accounts**: Generate an invoice for the order and record payments.
6.  **Dashboard**: Check how the stats update in real-time!

---

**Developed with ❤️ for Dental Excellence.**

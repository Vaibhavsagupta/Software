from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from typing import Optional

security = HTTPBearer(auto_error=False)

def get_current_user(token=Depends(security)):
    # 🔓 Authentication Disabled: Always return a dummy admin user
    return {"user_id": 1, "role": "admin"}

def admin_only(user=Depends(get_current_user)):
    # Always allow
    return user

def staff_only(user=Depends(get_current_user)):
    # Always allow
    return user

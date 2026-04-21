from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserLogin
from utils.security import hash_password, verify_password
from utils.jwt import create_token
from utils.deps import get_current_user, admin_only
from deps import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


# 📁 CREATE USER (ADMIN PANEL USE)
@router.post("/register")
def register(user: UserCreate, 
             db: Session = Depends(get_db),
             admin=Depends(admin_only)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)
    new_user = User(
        username=user.username,
        password=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}


# 🔑 LOGIN API
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        return {"error": "User not found"}

    if not verify_password(user.password, db_user.password):
        return {"error": "Wrong password"}

    token = create_token({
        "user_id": db_user.id,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "role": db_user.role
    }


# 🛡️ PROTECTED ROUTE TEST
@router.get("/secure-data")
def secure_data(user=Depends(get_current_user)):
    return {"msg": "You are logged in", "user": user}

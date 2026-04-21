from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Expense
from schemas import ExpenseCreate
from deps import get_db

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ➤ ADD EXPENSE
@router.post("/")
def add_expense(data: ExpenseCreate, db: Session = Depends(get_db)):

    expense = Expense(
        title=data.title,
        amount=data.amount
    )

    db.add(expense)
    db.commit()

    return {"msg": "Expense added"}


# ➤ GET ALL EXPENSES
@router.get("/")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()

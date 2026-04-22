from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import ProductCategory, ProductPrice
from schemas import ProductCategoryOut, ProductPriceOut
from deps import get_db
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/categories", response_model=List[ProductCategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(ProductCategory).all()

@router.get("/", response_model=List[ProductPriceOut])
def get_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProductPrice)
    if category_id:
        query = query.filter(ProductPrice.category_id == category_id)
    if search:
        query = query.filter(ProductPrice.name.ilike(f"%{search}%") | ProductPrice.code.ilike(f"%{search}%"))
    return query.all()

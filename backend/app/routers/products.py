from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Product
from ..database import get_session
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price_cents: int
    inventory: int = 0

@router.post("/", response_model=ProductCreate)
def create_product(p: ProductCreate, session: Session = Depends(get_session)):
    product = Product(**p.dict())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.get("/")
def list_products(session: Session = Depends(get_session)):
    stmt = select(Product)
    return session.exec(stmt).all()

@router.get("/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Order, OrderItem, Product, User
from ..database import get_session
from pydantic import BaseModel
from typing import List
from ..auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


@router.post("/")
def create_order(o: OrderCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # basic inventory check and order creation (requires auth)
    order = Order(user_id=current_user.id, status="pending")
    session.add(order)
    session.commit()
    session.refresh(order)
    total_cents = 0
    for it in o.items:
        product = session.get(Product, it.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {it.product_id} not found")
        if product.inventory < it.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient inventory for product {product.id}")
        product.inventory -= it.quantity
        session.add(product)
        item = OrderItem(order_id=order.id, product_id=product.id, quantity=it.quantity, unit_price_cents=product.price_cents)
        session.add(item)
        total_cents += product.price_cents * it.quantity
    order.status = "paid"  # mock: mark paid synchronously
    session.add(order)
    session.commit()
    return {"order_id": order.id, "total_cents": total_cents, "status": order.status}

@router.get("/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

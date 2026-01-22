from fastapi import FastAPI
from .database import engine
from .models import SQLModel
from .routers import users, products, orders

app = FastAPI(title="E-commerce Scaffold")

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers import auth, products, categories

app = FastAPI(title="Shop Insight API")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)


@app.get("/")
def home():
    return {"message": "Shop Insight Backend is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
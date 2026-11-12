from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy import text
from backend.database import get_db

app = FastAPI(title="Shop Insight API")


@app.get("/")
def home():
    return {"message": "Shop Insight Backend is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/health/db")
def health_db(db=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
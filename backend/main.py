from fastapi import FastAPI

app = FastAPI(title="Shop Insight API")


@app.get("/")
def home():
    return {"message": "Shop Insight Backend is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}
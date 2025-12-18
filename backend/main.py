from fastapi import FastAPI
from app.api import router

app = FastAPI(title="AI Proctoring System API")

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Proctoring System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

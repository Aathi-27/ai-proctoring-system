from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.database.mongodb import MongoDBClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDBClient.connect()
    yield
    await MongoDBClient.close()


app = FastAPI(
    title="Face Detection & Liveness Pipeline",
    description="Real-time face detection and liveness verification using MediaPipe",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["exams"])


@app.get("/")
async def root():
    return {
        "message": "Face Detection & Liveness Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "analyze_frame": "/api/v1/exams/{exam_id}/analyze-frame",
            "get_events": "/api/v1/exams/{exam_id}/events",
            "clear_history": "/api/v1/exams/{exam_id}/clear-history",
            "health": "/api/v1/health"
        }
    }

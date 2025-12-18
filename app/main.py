from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import risk_scoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Exam Proctoring Risk Scoring API",
    description="Rule-based risk scoring engine for exam proctoring with real-time updates",
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

app.include_router(risk_scoring.router)


@app.get("/")
async def root():
    return {
        "message": "Exam Proctoring Risk Scoring API",
        "version": "1.0.0",
        "endpoints": {
            "events": "POST /exams/{exam_id}/events",
            "compute_risk": "POST /exams/{exam_id}/compute-risk",
            "current_score": "GET /exams/{exam_id}/sessions/{session_id}/risk-score",
            "timeline": "GET /exams/{exam_id}/sessions/{session_id}/risk-timeline",
            "breakdown": "GET /exams/{exam_id}/sessions/{session_id}/score-breakdown",
            "websocket": "WS /exams/{exam_id}/ws"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

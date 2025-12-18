from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import db
from .websocket import websocket_endpoint

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    try:
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
    
    yield
    
    logger.info("Shutting down application...")
    await db.disconnect()


app = FastAPI(
    title="Exam Monitoring API",
    description="Real-time monitoring API for online exams with tab switching, copy-paste detection, and inactivity tracking",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Exam Monitoring API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_route(
    websocket: WebSocket,
    session_id: str = Query(None, description="Session ID for the exam")
):
    await websocket_endpoint(websocket, session_id)


@app.get("/api/events/session/{session_id}")
async def get_session_events(session_id: str, limit: int = 100):
    try:
        events = await db.get_events_by_session(session_id, limit)
        return {
            "session_id": session_id,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Failed to retrieve session events: {e}")
        return {"error": str(e)}, 500


@app.get("/api/events/candidate/{candidate_id}")
async def get_candidate_events(candidate_id: str, limit: int = 100):
    try:
        events = await db.get_events_by_candidate(candidate_id, limit)
        return {
            "candidate_id": candidate_id,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Failed to retrieve candidate events: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

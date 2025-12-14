from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from app.websocket.endpoints import router as websocket_router
from app.websocket.connection_manager import connection_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def ping_task():
    while True:
        await asyncio.sleep(30)
        await connection_manager.ping_connections()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WebSocket ping task...")
    ping_task_handle = asyncio.create_task(ping_task())
    
    yield
    
    logger.info("Shutting down...")
    ping_task_handle.cancel()
    try:
        await ping_task_handle
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Online Exam Proctoring WebSocket Server",
    description="WebSocket server for real-time media streaming and event handling",
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

app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "message": "Online Exam Proctoring WebSocket Server",
        "version": "1.0.0",
        "endpoints": {
            "invigilator": "/ws/exam/{exam_id}?invigilator_id={invigilator_id}",
            "candidate": "/ws/candidate/{session_id}?exam_id={exam_id}"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": connection_manager.get_active_connection_count()
    }


@app.get("/stats")
async def get_stats():
    return {
        "active_connections": connection_manager.get_active_connection_count(),
        "exam_rooms": {
            exam_id: len(candidates)
            for exam_id, candidates in connection_manager.exam_rooms.items()
        },
        "invigilator_connections": {
            exam_id: len(connections)
            for exam_id, connections in connection_manager.invigilator_connections.items()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

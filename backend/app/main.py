from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.websocket.endpoints import router as websocket_router
from app.websocket.connection_manager import connection_manager
import logging
import asyncio

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
    """Application lifespan events."""
    # Database init
    from app.db.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # MongoDB init
    from app.db.mongodb import MongoDBClient
    await MongoDBClient.connect()
    
    # WebSocket ping task
    logger.info("Starting WebSocket ping task...")
    ping_task_handle = asyncio.create_task(ping_task())
    
    yield
    
    logger.info("Shutting down...")
    ping_task_handle.cancel()
    try:
        await ping_task_handle
    except asyncio.CancelledError:
        pass
        
    await MongoDBClient.close()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket_router)

@app.get("/")
def root():
    return {
        "message": "Exam Proctoring System API",
        "endpoints": {
            "api": settings.API_V1_PREFIX,
            "websocket_invigilator": "/ws/exam/{exam_id}?invigilator_id={invigilator_id}",
            "websocket_candidate": "/ws/candidate/{session_id}?exam_id={exam_id}"
        }
    }

@app.get("/health")
def health_check():
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

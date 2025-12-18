import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router as face_detection_router
from app.api.websocket_routes import router as websocket_router
from app.database.mongodb import mongodb_client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        # Connect to MongoDB
        await mongodb_client.connect()
        logger.info("MongoDB connection established")
        
        yield
        
    except Exception as e:
        logger.error(f"Application startup error: {e}")
        raise
    finally:
        # Cleanup
        await mongodb_client.close()
        logger.info("Application shutdown completed")


app = FastAPI(
    title="AI Proctoring System",
    description="Real-time AI proctoring with WebSocket alerts, evidence capture, and risk scoring",
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

# Include routers
app.include_router(face_detection_router, prefix="/api/v1", tags=["face-detection"])
app.include_router(websocket_router, prefix="/api/v1", tags=["alerts", "websocket"])


@app.get("/")
async def root():
    return {
        "message": "AI Proctoring System API",
        "version": "1.0.0",
        "services": {
            "face_detection": "Real-time face detection and liveness verification",
            "websocket_alerts": "WebSocket-based real-time alert system",
            "evidence_capture": "Encrypted evidence snapshot storage",
            "risk_scoring": "Dynamic risk scoring with temporal decay"
        },
        "endpoints": {
            "face_detection": "/api/v1/exams/{exam_id}/analyze-frame",
            "websocket": "/api/v1/ws/exam/{exam_id}",
            "alerts": "/api/v1/exams/{exam_id}/alerts",
            "health": "/api/v1/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if mongodb_client.is_connected() else "disconnected",
        "services": {
            "mongodb": "active" if mongodb_client.is_connected() else "inactive",
            "websocket_manager": "active",
            "alert_service": "active",
            "evidence_service": "active"
        },
        "timestamp": "2025-01-15T14:23:45Z"
    }
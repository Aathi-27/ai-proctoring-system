"""
FastAPI endpoints for YOLOv8 object detection system.

REST API endpoints for processing frames and managing detection events.
"""

import base64
import io
import time
from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
from loguru import logger

from ..detection.yolov8_detector import YOLOv8Detector, DetectionResult, DetectionEvent
from ..database.event_storage import event_storage
from ..config.settings import detection_config, api_config
from ..models import ProcessFrameResponse, APIResponse


# Initialize FastAPI app
app = FastAPI(
    title="YOLOv8 Mobile Detection API",
    description="Real-time mobile phone and object detection for exam monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global detector instance
detector = None


def get_detector() -> YOLOv8Detector:
    """Dependency to get detector instance."""
    global detector
    if detector is None:
        logger.info("Initializing YOLOv8 detector...")
        detector = YOLOv8Detector(detection_config)
        logger.info("YOLOv8 detector initialized")
    return detector


def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode base64 image data to numpy array."""
    try:
        # Remove data URL prefix if present
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert to numpy array
        return np.array(image)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting YOLOv8 Detection API...")
    
    try:
        # Initialize detector
        global detector
        detector = YOLOv8Detector(detection_config)
        
        # Connect to MongoDB
        await event_storage.connect()
        
        logger.info("YOLOv8 Detection API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down YOLOv8 Detection API...")
    
    try:
        # Disconnect from MongoDB
        await event_storage.disconnect()
        
        logger.info("YOLOv8 Detection API shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        detector_instance = get_detector()
        
        services = {
            "yolov8_detector": {
                "status": "healthy" if detector_instance.model else "unhealthy",
                "model_loaded": detector_instance.model is not None,
                "performance_stats": detector_instance.get_performance_stats()
            },
            "mongodb": await event_storage.health_check(),
            "api": {
                "status": "healthy",
                "timestamp": time.time()
            }
        }
        
        # Determine overall status
        overall_status = "healthy"
        for service_name, service_info in services.items():
            if service_info.get("status") != "healthy":
                overall_status = "unhealthy"
                break
        
        return APIResponse(
            success=True,
            message=f"System status: {overall_status}",
            data=services
        ).to_dict()
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            success=False,
            message="Health check failed",
            data={"error": str(e)}
        ).to_dict()


@app.post("/exams/{exam_id}/detect-objects", response_model=Dict[str, Any])
async def detect_objects(
    exam_id: str,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    detector_instance: YOLOv8Detector = Depends(get_detector)
):
    """
    Detect objects in an uploaded image frame.
    
    Args:
        exam_id: Exam identifier
        image: Uploaded image file
        background_tasks: Background task manager
        detector_instance: YOLOv8 detector instance
    
    Returns:
        Detection results and events
    """
    start_time = time.time()
    
    try:
        # Validate file extension
        file_extension = "." + image.filename.split(".")[-1].lower()
        if file_extension not in api_config.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed"
            )
        
        # Read and validate image
        image_data = await image.read()
        
        # Check file size
        file_size_mb = len(image_data) / (1024 * 1024)
        if file_size_mb > api_config.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {api_config.max_file_size_mb}MB"
            )
        
        # Convert to numpy array
        try:
            pil_image = Image.open(io.BytesIO(image_data))
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            image_array = np.array(pil_image)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Run detection
        detections = detector_instance.detect_objects(image_array, exam_id)
        
        # Create events
        events = []
        for detection in detections:
            event = detector_instance.create_detection_event(detection, exam_id)
            events.append(event)
        
        # Store events in background (don't wait for completion)
        if events:
            background_tasks.add_task(
                event_storage.store_events_batch, events
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        response = ProcessFrameResponse(
            detected_objects=detections,
            events=events,
            processing_time_ms=processing_time_ms
        )
        
        logger.info(
            f"Processed frame for exam {exam_id}: "
            f"{len(detections)} detections, {len(events)} events"
        )
        
        return response.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing frame for exam {exam_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/exams/{exam_id}/detect-objects/base64")
async def detect_objects_base64(
    exam_id: str,
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    detector_instance: YOLOv8Detector = Depends(get_detector)
):
    """
    Detect objects in a base64-encoded image.
    
    Args:
        exam_id: Exam identifier
        request: Request containing base64 image data
        background_tasks: Background task manager
        detector_instance: YOLOv8 detector instance
    
    Returns:
        Detection results and events
    """
    start_time = time.time()
    
    try:
        # Extract image data
        image_data = request.get("image_data")
        if not image_data:
            raise HTTPException(status_code=400, detail="image_data is required")
        
        # Decode base64 image
        image_array = decode_base64_image(image_data)
        
        # Run detection
        detections = detector_instance.detect_objects(image_array, exam_id)
        
        # Create events
        events = []
        for detection in detections:
            event = detector_instance.create_detection_event(detection, exam_id)
            events.append(event)
        
        # Store events in background
        if events:
            background_tasks.add_task(
                event_storage.store_events_batch, events
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        response = ProcessFrameResponse(
            detected_objects=detections,
            events=events,
            processing_time_ms=processing_time_ms
        )
        
        return response.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing base64 frame for exam {exam_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/exams/{exam_id}/events")
async def get_exam_events(
    exam_id: str,
    event_type: str = None,
    limit: int = 1000
):
    """Get detection events for a specific exam."""
    try:
        events = await event_storage.get_events(
            exam_id=exam_id,
            event_type=event_type,
            limit=limit
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(events)} events",
            data={"events": events}
        ).to_dict()
        
    except Exception as e:
        logger.error(f"Error retrieving events for exam {exam_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@app.get("/performance/metrics")
async def get_performance_metrics(detector_instance: YOLOv8Detector = Depends(get_detector)):
    """Get performance metrics from the detector."""
    try:
        metrics = detector_instance.get_performance_stats()
        
        return APIResponse(
            success=True,
            message="Retrieved performance metrics",
            data=metrics
        ).to_dict()
        
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug,
        log_level="info"
    )
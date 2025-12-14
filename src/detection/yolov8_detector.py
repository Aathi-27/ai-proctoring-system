"""
YOLOv8-based mobile phone and object detection system.

Real-time object detection for exam monitoring, focusing on mobile phones,
tablets, laptops, notebooks, and people with advanced filtering.
"""

import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque
from loguru import logger

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Install with: pip install opencv-python")
    # Create dummy numpy for when OpenCV is not available
    try:
        import numpy as np
    except ImportError:
        np = None
        logger.warning("NumPy not available. Install with: pip install numpy")

try:
    from ultralytics import YOLO
    YOLOv8_AVAILABLE = True
except ImportError:
    YOLOv8_AVAILABLE = False
    logger.warning("YOLOv8 not available. Install with: pip install ultralytics")


@dataclass
class DetectionResult:
    """Result from object detection."""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    area_ratio: float
    timestamp: float
    frame_id: Optional[int] = None


@dataclass
class DetectionEvent:
    """Event generated from detection results."""
    event_type: str
    object_type: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    timestamp: float
    frame_id: Optional[int] = None
    risk_score: int = 0
    metadata: Optional[Dict] = None


class TemporalFilter:
    """Temporal filtering to reduce false positives."""
    
    def __init__(self, window_size: int = 3, min_consecutive: int = 2):
        self.window_size = window_size
        self.min_consecutive = min_consecutive
        self.detection_history: Dict[str, deque] = {}
        self.confidence_history: Dict[str, deque] = {}
    
    def add_detection(self, class_name: str, confidence: float, bbox: Tuple[int, int, int, int]):
        """Add a new detection to the temporal filter."""
        if class_name not in self.detection_history:
            self.detection_history[class_name] = deque(maxlen=self.window_size)
            self.confidence_history[class_name] = deque(maxlen=self.window_size)
        
        self.detection_history[class_name].append(True)
        self.confidence_history[class_name].append(confidence)
    
    def should_alert(self, class_name: str, current_confidence: float) -> Tuple[bool, float]:
        """Determine if an alert should be triggered based on temporal filtering."""
        if class_name not in self.detection_history:
            return False, 0.0
        
        # Check if object was detected in enough consecutive frames
        detection_window = list(self.detection_history[class_name])
        consecutive_count = self._count_consecutive_true(detection_window)
        
        if consecutive_count < self.min_consecutive:
            return False, 0.0
        
        # Calculate average confidence over the window
        avg_confidence = np.mean(list(self.confidence_history[class_name]))
        
        # Only alert if average confidence is above threshold
        if avg_confidence >= 0.5:
            return True, avg_confidence
        
        return False, avg_confidence
    
    def _count_consecutive_true(self, detection_window: List[bool]) -> int:
        """Count consecutive True values from the end of the window."""
        count = 0
        for value in reversed(detection_window):
            if value:
                count += 1
            else:
                break
        return count


class FalsePositiveFilter:
    """Filter to suppress known false positives."""
    
    def __init__(self):
        self.suppress_classes = ["tv", "monitor", "keyboard"]
    
    def should_suppress(self, class_name: str, bbox: Tuple[int, int, int, int], 
                       area_ratio: float, image_shape: Tuple[int, int]) -> bool:
        """Determine if a detection should be suppressed as a false positive."""
        height, width = image_shape[:2]
        
        # Suppress known false positive classes
        if class_name in self.suppress_classes:
            # But allow small devices (might be phones that look like screens)
            if class_name in ["tv", "monitor"] and area_ratio < 0.3:
                return False
            return True
        
        # Suppress very small or very large detections
        if area_ratio < 0.001 or area_ratio > 0.8:
            return True
        
        # Check if detection is at image boundaries (likely camera frame)
        x, y, w, h = bbox
        if (x < 10 or y < 10 or x + w > width - 10 or y + h > height - 10):
            if class_name in ["person", "laptop"]:
                return True
        
        return False


class YOLOv8Detector:
    """YOLOv8-based object detector for exam monitoring."""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.frame_count = 0
        self.temporal_filter = TemporalFilter(
            window_size=config.temporal_window,
            min_consecutive=config.min_consecutive_frames
        )
        self.false_positive_filter = FalsePositiveFilter()
        self.performance_stats = {
            "total_frames": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0
        }
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the YOLOv8 model."""
        if not YOLOv8_AVAILABLE:
            logger.warning("YOLOv8 not available. Running in mock mode.")
            return
        
        try:
            logger.info(f"Loading YOLOv8 model: {self.config.model_name}")
            
            # Load model
            self.model = YOLO(self.config.model_name)
            
            # Apply optimizations
            if self.config.use_fp16:
                logger.info("Enabling FP16 precision for CPU optimization")
                self.model.model.float()
            
            # Warm up model
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(dummy_image, verbose=False)
            
            logger.info("YOLOv8 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            logger.warning("Running in mock mode without actual model")
            self.model = None
    
    def detect_objects(self, image: np.ndarray, exam_id: Optional[str] = None) -> List[DetectionResult]:
        """
        Detect objects in the given image.
        
        Args:
            image: Input image as numpy array
            exam_id: Optional exam identifier for logging
        
        Returns:
            List of DetectionResult objects
        """
        start_time = time.time()
        
        # Skip frames based on frame skip ratio
        self.frame_count += 1
        if self.frame_count % self.config.frame_skip_ratio != 0:
            return []
        
        # If no model available, return empty results
        if self.model is None:
            return []
        
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Run YOLOv8 inference
            results = self.model(
                processed_image,
                conf=self.config.model_confidence_threshold,
                verbose=False
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    # Extract detection information
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[cls]
                    
                    # Only process target classes
                    if class_name not in self.config.target_classes:
                        continue
                    
                    # Calculate bounding box and area ratio
                    bbox_width = int(xyxy[2] - xyxy[0])
                    bbox_height = int(xyxy[3] - xyxy[1])
                    bbox = (int(xyxy[0]), int(xyxy[1]), bbox_width, bbox_height)
                    
                    area_ratio = (bbox_width * bbox_height) / (image.shape[0] * image.shape[1])
                    
                    # Check for false positives
                    if self.false_positive_filter.should_suppress(
                        class_name, bbox, area_ratio, image.shape
                    ):
                        continue
                    
                    # Add to temporal filter
                    self.temporal_filter.add_detection(class_name, conf, bbox)
                    
                    # Check temporal filtering
                    should_alert, avg_confidence = self.temporal_filter.should_alert(class_name, conf)
                    
                    if should_alert:
                        detection = DetectionResult(
                            class_name=class_name,
                            confidence=avg_confidence,
                            bbox=bbox,
                            area_ratio=area_ratio,
                            timestamp=time.time(),
                            frame_id=self.frame_count
                        )
                        detections.append(detection)
            
            # Update performance stats
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_stats(processing_time)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for YOLOv8 inference."""
        if not CV2_AVAILABLE or np is None:
            # Return dummy processed image
            target_width, target_height = self.config.input_size
            return np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # Resize image to target size
        target_width, target_height = self.config.input_size
        
        # Calculate scaling factor to maintain aspect ratio
        height, width = image.shape[:2]
        scale = min(target_width / width, target_height / height)
        
        # Calculate new size
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Create padded image
        padded = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # Calculate padding
        pad_x = (target_width - new_width) // 2
        pad_y = (target_height - new_height) // 2
        
        # Place resized image in center
        padded[pad_y:pad_y + new_height, pad_x:pad_x + new_width] = resized
        
        return padded
    
    def _update_performance_stats(self, processing_time_ms: float):
        """Update performance statistics."""
        self.performance_stats["total_frames"] += 1
        self.performance_stats["total_processing_time"] += processing_time_ms
        self.performance_stats["avg_processing_time"] = (
            self.performance_stats["total_processing_time"] / 
            self.performance_stats["total_frames"]
        )
    
    def get_risk_score(self, class_name: str) -> int:
        """Get risk score for detected object class."""
        risk_scores = {
            "mobile_phone": self.config.mobile_phone_risk_points,
            "tablet": self.config.tablet_risk_points,
            "laptop": self.config.laptop_risk_points,
            "notebook": self.config.notebook_risk_points,
            "person": 0
        }
        return risk_scores.get(class_name, 0)
    
    def create_detection_event(self, detection: DetectionResult, exam_id: str) -> DetectionEvent:
        """Create a detection event from a detection result."""
        risk_score = self.get_risk_score(detection.class_name)
        
        # Determine event type based on class
        if detection.class_name == "mobile_phone":
            event_type = "MOBILE_DETECTED"
        elif detection.class_name == "tablet":
            event_type = "TABLET_DETECTED"
        else:
            event_type = "SUSPICIOUS_OBJECT"
        
        return DetectionEvent(
            event_type=event_type,
            object_type=detection.class_name,
            confidence=detection.confidence,
            bbox=detection.bbox,
            timestamp=detection.timestamp,
            frame_id=detection.frame_id,
            risk_score=risk_score,
            metadata={
                "exam_id": exam_id,
                "area_ratio": detection.area_ratio
            }
        )
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        stats = self.performance_stats.copy()
        if stats["total_frames"] > 0:
            stats["fps"] = 1000.0 / stats["avg_processing_time"]
        else:
            stats["fps"] = 0.0
        return stats
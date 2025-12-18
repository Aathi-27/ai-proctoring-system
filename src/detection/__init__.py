# Detection module initialization
from .yolov8_detector import YOLOv8Detector, DetectionResult, DetectionEvent, TemporalFilter, FalsePositiveFilter

__all__ = [
    "YOLOv8Detector",
    "DetectionResult", 
    "DetectionEvent",
    "TemporalFilter",
    "FalsePositiveFilter"
]
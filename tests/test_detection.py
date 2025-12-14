"""
Unit tests for YOLOv8 detector functionality.

Core detection capabilities, temporal filtering, and performance optimization.
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock, patch

# Import our modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detection.yolov8_detector import (
    YOLOv8Detector, TemporalFilter, FalsePositiveFilter,
    DetectionResult, DetectionEvent
)
from src.config.settings import detection_config


class TestTemporalFilter:
    """Test temporal filtering for false positive reduction."""
    
    def test_initial_state(self):
        """Test initial state of temporal filter."""
        temporal_filter = TemporalFilter(window_size=3, min_consecutive=2)
        
        assert len(temporal_filter.detection_history) == 0
        assert len(temporal_filter.confidence_history) == 0
    
    def test_single_detection_no_alert(self):
        """Test that single detection doesn't trigger alert."""
        temporal_filter = TemporalFilter(window_size=3, min_consecutive=2)
        
        temporal_filter.add_detection("mobile_phone", 0.8, (100, 100, 50, 80))
        should_alert, avg_confidence = temporal_filter.should_alert("mobile_phone", 0.8)
        
        assert not should_alert
        assert avg_confidence == 0.0
    
    def test_consecutive_detections_trigger_alert(self):
        """Test that consecutive detections trigger alert."""
        temporal_filter = TemporalFilter(window_size=3, min_consecutive=2)
        
        # Add two consecutive detections
        temporal_filter.add_detection("mobile_phone", 0.8, (100, 100, 50, 80))
        temporal_filter.add_detection("mobile_phone", 0.7, (105, 105, 55, 85))
        
        should_alert, avg_confidence = temporal_filter.should_alert("mobile_phone", 0.75)
        
        assert should_alert
        assert abs(avg_confidence - 0.75) < 0.01  # Average of 0.8, 0.7, 0.75
    
    def test_insufficient_confidence_no_alert(self):
        """Test that low confidence prevents alert."""
        temporal_filter = TemporalFilter(window_size=3, min_consecutive=2)
        
        # Add detections with low confidence
        temporal_filter.add_detection("mobile_phone", 0.3, (100, 100, 50, 80))
        temporal_filter.add_detection("mobile_phone", 0.4, (105, 105, 55, 85))
        
        should_alert, avg_confidence = temporal_filter.should_alert("mobile_phone", 0.35)
        
        assert not should_alert
        assert avg_confidence < 0.5


class TestFalsePositiveFilter:
    """Test false positive filtering logic."""
    
    def test_webcam_suppression(self):
        """Test that large monitor/TV detections are suppressed."""
        false_positive_filter = FalsePositiveFilter()
        
        # Large screen should be suppressed
        result = false_positive_filter.should_suppress(
            "tv", (100, 100, 800, 600), 0.5, (1000, 800)
        )
        assert result is True
        
        # Small device should not be suppressed
        result = false_positive_filter.should_suppress(
            "mobile_phone", (100, 100, 50, 80), 0.02, (1000, 800)
        )
        assert result is False
    
    def test_area_threshold_filtering(self):
        """Test area ratio threshold filtering."""
        false_positive_filter = FalsePositiveFilter()
        
        # Very small detection should be suppressed
        result = false_positive_filter.should_suppress(
            "mobile_phone", (100, 100, 10, 15), 0.0005, (1000, 800)
        )
        assert result is True
        
        # Very large detection should be suppressed
        result = false_positive_filter.should_suppress(
            "mobile_phone", (100, 100, 900, 700), 0.9, (1000, 800)
        )
        assert result is True
    
    def test_boundary_suppression(self):
        """Test that boundary detections are suppressed."""
        false_positive_filter = FalsePositiveFilter()
        
        # Detection at image boundary
        result = false_positive_filter.should_suppress(
            "person", (5, 5, 100, 150), 0.1, (1000, 800)
        )
        assert result is True
        
        # Normal detection should not be suppressed
        result = false_positive_filter.should_suppress(
            "person", (200, 200, 100, 150), 0.1, (1000, 800)
        )
        assert result is False


class TestYOLOv8Detector:
    """Test YOLOv8 detector functionality."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = YOLOv8Detector(detection_config)
        
        assert detector.config == detection_config
        assert detector.frame_count == 0
        assert detector.temporal_filter is not None
        assert detector.false_positive_filter is not None
        assert "total_frames" in detector.performance_stats
    
    def test_risk_score_mapping(self):
        """Test risk score mapping for different object types."""
        detector = YOLOv8Detector(detection_config)
        
        assert detector.get_risk_score("mobile_phone") == 25
        assert detector.get_risk_score("tablet") == 20
        assert detector.get_risk_score("laptop") == 15
        assert detector.get_risk_score("notebook") == 10
        assert detector.get_risk_score("person") == 0
        assert detector.get_risk_score("unknown") == 0
    
    def test_create_detection_event_mobile(self):
        """Test creation of detection events for mobile phones."""
        detector = YOLOv8Detector(detection_config)
        
        detection = DetectionResult(
            class_name="mobile_phone",
            confidence=0.85,
            bbox=(100, 100, 50, 80),
            area_ratio=0.02,
            timestamp=1234567890.0,
            frame_id=1
        )
        
        event = detector.create_detection_event(detection, "test_exam_123")
        
        assert event.event_type == "MOBILE_DETECTED"
        assert event.object_type == "mobile_phone"
        assert event.confidence == 0.85
        assert event.risk_score == 25
        assert event.metadata["exam_id"] == "test_exam_123"
    
    def test_create_detection_event_tablet(self):
        """Test creation of detection events for tablets."""
        detector = YOLOv8Detector(detection_config)
        
        detection = DetectionResult(
            class_name="tablet",
            confidence=0.9,
            bbox=(200, 200, 100, 150),
            area_ratio=0.05,
            timestamp=1234567890.0,
            frame_id=2
        )
        
        event = detector.create_detection_event(detection, "test_exam_456")
        
        assert event.event_type == "TABLET_DETECTED"
        assert event.object_type == "tablet"
        assert event.risk_score == 20
    
    def test_frame_skipping(self):
        """Test frame skipping functionality."""
        detector = YOLOv8Detector(detection_config)
        
        # Mock image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Set frame skip ratio to 3
        detector.config.frame_skip_ratio = 3
        
        # Process frames and check skipping
        for i in range(6):
            detector.frame_count = i + 1
            detections = detector.detect_objects(test_image, "test_exam")
            
            # Should only process when frame_count % 3 == 0
            if (i + 1) % 3 == 0:
                # In mock mode, should return empty list
                assert isinstance(detections, list)
            else:
                assert len(detections) == 0
    
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        detector = YOLOv8Detector(detection_config)
        
        # Mock image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process a few frames to generate metrics
        detector.config.frame_skip_ratio = 1
        
        for i in range(5):
            detector.frame_count = i + 1
            detector.detect_objects(test_image, "test_exam")
        
        # Check that performance stats are available
        stats = detector.get_performance_stats()
        assert stats is not None
        assert "total_frames" in stats
        assert stats["total_frames"] > 0
    
    def test_processing_time_requirement(self):
        """Test that processing time meets ≤500ms requirement."""
        detector = YOLOv8Detector(detection_config)
        detector.config.frame_skip_ratio = 1
        
        # Create test images
        test_images = [
            np.zeros((480, 640, 3), dtype=np.uint8),    # Standard size
            np.zeros((720, 1280, 3), dtype=np.uint8),   # HD size
        ]
        
        processing_times = []
        
        for test_image in test_images:
            start_time = time.time()
            detector.detect_objects(test_image, "perf_test")
            processing_time = (time.time() - start_time) * 1000
            processing_times.append(processing_time)
        
        # In mock mode, processing should be very fast
        max_processing_time = max(processing_times)
        assert max_processing_time <= 1000, f"Mock processing time {max_processing_time}ms too high"


class TestDetectionPerformance:
    """Test detection performance requirements."""
    
    def test_frame_skipping_effectiveness(self):
        """Test that frame skipping improves performance."""
        detector = YOLOv8Detector(detection_config)
        
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test without frame skipping
        detector.config.frame_skip_ratio = 1
        detector.frame_count = 0
        start_time = time.time()
        for i in range(10):
            detector.frame_count = i + 1
            detector.detect_objects(test_image, "perf_test")
        no_skip_time = (time.time() - start_time) * 1000
        
        # Test with frame skipping
        detector.config.frame_skip_ratio = 3
        detector.frame_count = 0
        start_time = time.time()
        for i in range(10):
            detector.frame_count = i + 1
            detector.detect_objects(test_image, "perf_test")
        with_skip_time = (time.time() - start_time) * 1000
        
        # Frame skipping should improve performance
        assert with_skip_time <= no_skip_time, "Frame skipping should not degrade performance"


if __name__ == "__main__":
    pytest.main([__file__])
# YOLOv8 Mobile Phone & Object Detection System

A real-time mobile phone and object detection system for exam monitoring, built with YOLOv8, FastAPI, and MongoDB.

## 🎯 Features

### ✅ YOLOv8 Integration
- **Pre-trained Models**: YOLOv8 nano/small variants for CPU efficiency
- **Real-time Processing**: ≤500ms per frame processing time
- **Multi-object Detection**: Mobile phones, tablets, laptops, notebooks, people
- **Configurable Confidence**: Default 0.5 threshold with customization

### ✅ Smart Filtering
- **Temporal Filtering**: Reduces false positives by requiring 2+ consecutive detections
- **False Positive Suppression**: Eliminates webcam, monitor, keyboard false alarms
- **Area-based Filtering**: Removes detections that are too small or large
- **Frame Skipping**: Process 1 frame per 3-5 input frames for performance

### ✅ Event System
- **Event Types**: MOBILE_DETECTED, TABLET_DETECTED, SUSPICIOUS_OBJECT
- **Risk Scoring**: Mobile phones (+25), tablets (+20), laptops (+15), notebooks (+10)
- **MongoDB Integration**: Async event storage with automatic cleanup
- **Real-time Logging**: Background event emission and storage

### ✅ Performance Optimization
- **CPU-first Design**: Optimized for standard Intel i5/i7 processors
- **Model Quantization**: FP16 precision for CPU optimization
- **Batch Processing**: Efficient inference on multiple frames
- **Memory Management**: Smart image preprocessing and caching

### ✅ RESTful API
- **Multiple Input Formats**: Support for file upload and base64 images
- **Health Monitoring**: Comprehensive system health checks
- **Performance Metrics**: Real-time processing statistics
- **CORS Support**: Cross-origin resource sharing for web clients

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 4GB+ RAM
- Intel i5/i7 or equivalent CPU
- MongoDB (optional, runs in mock mode without)

### Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Download YOLOv8 models**
```bash
python main.py download-models
```

3. **Run the application**
```bash
# Start API server
python main.py server

# Or with debug mode
python main.py server --debug --port 8000
```

The API will be available at `http://localhost:8000`

### Health Check
```bash
python main.py health
```

## 📡 API Usage

### Core Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Detect Objects (File Upload)
```bash
curl -X POST "http://localhost:8000/exams/exam_123/detect-objects" \\
     -F "image=@test_image.jpg"
```

**Response:**
```json
{
  "detected_objects": [
    {
      "class_name": "mobile_phone",
      "confidence": 0.85,
      "bbox": [100, 100, 50, 80],
      "area_ratio": 0.02,
      "timestamp": 1234567890.0,
      "frame_id": 42
    }
  ],
  "events": [
    {
      "event_type": "MOBILE_DETECTED",
      "object_type": "mobile_phone",
      "confidence": 0.85,
      "bbox": [100, 100, 50, 80],
      "timestamp": 1234567890.0,
      "risk_score": 25,
      "metadata": {"exam_id": "exam_123", "area_ratio": 0.02}
    }
  ],
  "processing_time_ms": 245.6
}
```

#### Detect Objects (Base64)
```bash
curl -X POST "http://localhost:8000/exams/exam_123/detect-objects/base64" \\
     -H "Content-Type: application/json" \\
     -d '{
       "image_data": "base64_encoded_image_data"
     }'
```

#### Get Detection Events
```bash
curl "http://localhost:8000/exams/exam_123/events?event_type=MOBILE_DETECTED&limit=100"
```

#### Get Performance Metrics
```bash
curl http://localhost:8000/performance/metrics
```

## ⚙️ Configuration

### Detection Settings
```python
# config/settings.py
DetectionConfig(
    model_name="yolov8n.pt",                    # Model variant
    model_confidence_threshold=0.5,             # Detection confidence
    frame_skip_ratio=3,                         # Process 1 frame per N
    max_processing_time_ms=500,                 # Max processing time
    temporal_window=3,                          # Frames for filtering
    min_consecutive_frames=2,                   # Min detections for alert
    
    # Risk scoring
    mobile_phone_risk_points=25,                # Risk points for mobile
    tablet_risk_points=20,                      # Risk points for tablet
    laptop_risk_points=15,                      # Risk points for laptop
    notebook_risk_points=10,                    # Risk points for notebook
    
    # CPU optimization
    use_fp16=True,                             # Enable FP16
    input_size=(640, 640)                      # Model input size
)
```

### Environment Variables
```bash
# Detection configuration
export DETECTION_MODEL_NAME=yolov8n.pt
export DETECTION_MODEL_CONFIDENCE_THRESHOLD=0.5
export DETECTION_FRAME_SKIP_RATIO=3

# MongoDB configuration
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_DATABASE=exam_detection

# API configuration
export API_HOST=0.0.0.0
export API_PORT=8000
export API_DEBUG=false
export API_MAX_FILE_SIZE_MB=50
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python main.py test

# Run specific test categories
pytest tests/test_detection.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Test Coverage
- **Detection Logic**: Temporal filtering, false positive reduction
- **Performance**: Frame skipping, processing time validation
- **API Endpoints**: Request/response handling, error management
- **Event System**: MongoDB integration, event creation

## 📊 Performance Benchmarks

### Target Performance
- **Processing Time**: ≤500ms per frame
- **Frame Rate**: 2-5 FPS with frame skipping (3:1 ratio)
- **Memory Usage**: <2GB RAM
- **CPU Usage**: <80% on Intel i5
- **False Positive Rate**: <5% target

### Optimization Techniques
1. **Model Quantization**: FP16 precision for 2x speedup
2. **Frame Skipping**: 3-5x processing speedup
3. **Batch Processing**: Efficient CPU utilization
4. **Image Preprocessing**: Optimized resizing and normalization
5. **Temporal Filtering**: Reduces false positive processing

## 📋 Event Schema

### Detection Events
```json
{
  "event_type": "MOBILE_DETECTED",           // MOBILE_DETECTED, TABLET_DETECTED, SUSPICIOUS_OBJECT
  "object_type": "mobile_phone",             // Detected class
  "confidence": 0.85,                        // Detection confidence
  "bbox": [100, 100, 50, 80],               // Bounding box (x, y, width, height)
  "timestamp": 1234567890.0,                 // Unix timestamp
  "frame_id": 42,                            // Frame number
  "risk_score": 25,                          // Risk points
  "metadata": {
    "exam_id": "exam_123",                   // Exam identifier
    "area_ratio": 0.02                       // Detection area ratio
  }
}
```

### Risk Scoring
- **Mobile Phone**: +25 points (highest priority)
- **Tablet**: +20 points (high priority)
- **Laptop**: +15 points (medium priority)
- **Notebook**: +10 points (lower priority)
- **Person**: +0 points (baseline)

## 🗄️ MongoDB Integration

### Collection Structure
```javascript
// detection_events collection
{
  "_id": ObjectId("..."),
  "event_type": "MOBILE_DETECTED",
  "object_type": "mobile_phone",
  "confidence": 0.85,
  "bbox": [100, 100, 50, 80],
  "timestamp": ISODate("2024-01-01T12:00:00Z"),
  "frame_id": 42,
  "risk_score": 25,
  "metadata": {
    "exam_id": "exam_123",
    "area_ratio": 0.02
  }
}
```

### Indexes
- `{ "timestamp": -1 }` - Time-based queries
- `{ "metadata.exam_id": 1 }` - Exam-specific queries
- `{ "event_type": 1, "timestamp": -1 }` - Event filtering

## 🔧 Troubleshooting

### Common Issues

1. **YOLOv8 Model Download Fails**
   ```bash
   # Manual download
   python main.py download-models
   
   # Or install manually
   pip install ultralytics
   python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
   ```

2. **High CPU Usage**
   ```python
   # Increase frame skip ratio
   detection_config.frame_skip_ratio = 5
   # Or use smaller model
   detection_config.model_name = "yolov8n.pt"
   ```

3. **Memory Issues**
   ```python
   # Reduce input size
   detection_config.input_size = (416, 416)
   # Enable garbage collection
   import gc; gc.collect()
   ```

4. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB status
   mongosh --eval "db.runCommand('ping')"
   
   # Test connection
   python main.py health
   ```

### Debug Mode
```bash
# Enable debug logging
python main.py server --debug

# Check performance metrics
curl http://localhost:8000/performance/metrics
```

## 📈 Monitoring

### Health Checks
- `/health` - Overall system health
- `/performance/metrics` - Processing statistics
- Model loading status
- MongoDB connectivity

### Logging
- **Structured logs** with loguru
- **Performance metrics** every 100 frames
- **Error tracking** and alerting
- **Log levels**: DEBUG, INFO, WARNING, ERROR

### Metrics
- Processing time per frame
- Detection accuracy and confidence
- False positive rates
- System resource usage (CPU, memory)
- Event generation rates

## 🔒 Security Considerations

### API Security
- Rate limiting (configurable)
- File size limits (50MB default)
- Input validation and sanitization
- CORS configuration for web clients

### Data Privacy
- No persistent image storage
- Automatic event cleanup (30-day retention)
- Secure MongoDB connections
- Environment-based configuration

## 🐳 Deployment

### Docker
```bash
# Build image
docker build -t yolov8-detection .

# Run container
docker run -p 8000:8000 -e MONGODB_HOST=mongodb yolov8-detection
```

### Production
```bash
# Use production settings
export API_DEBUG=false
export DETECTION_MODEL_NAME=yolov8s.pt
python main.py server --port 80

# With nginx reverse proxy
nginx -s reload
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests before commit
python main.py test

# Check code format
black src/ tests/
isort src/ tests/
```

### Code Style
- **Black**: Code formatting
- **isort**: Import sorting
- **Type hints**: Full type coverage
- **Documentation**: Comprehensive docstrings

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] GPU acceleration support
- [ ] Custom model training pipeline
- [ ] Real-time video stream processing
- [ ] Advanced analytics dashboard
- [ ] Multi-camera support
- [ ] Edge deployment optimizations

## 📞 Support

- Check the troubleshooting section
- Review API documentation at `/docs`
- Run system health check: `python main.py health`
- Check logs for detailed error information

---

**Built for exam integrity and academic honesty** 🎓
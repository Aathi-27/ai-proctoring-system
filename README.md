# Audio Processing & Voice Detection Pipeline

Real-time Voice Activity Detection (VAD), background speech detection, and multiple voice detection for audio stream analysis.

## Features

### Core Components

- **Real-time Voice Activity Detection (VAD)**
  - Silero VAD library for lightweight, real-time voice detection
  - 16 kHz sampling rate, mono channel
  - 32ms frame-based analysis
  - VAD score (0-1): Probability of speech presence
  - Low latency (<100ms), CPU-efficient

- **Background Speech Detection**
  - Detects non-candidate voices in the audio stream
  - BACKGROUND_SPEECH event with confidence score
  - Based on acoustic features (spectral analysis)
  - Logged to MongoDB

- **Multiple Voices Detection**
  - Detects 2+ distinct speakers
  - MULTIPLE_VOICES event with speaker count
  - Voice separation using spectral features
  - Energy-based speaker count estimation
  - Temporal tracking over 5+ second window

- **Audio Event Emission**
  - VAD_DETECTED: {confidence, timestamp}
  - SPEECH_SILENCE_RATIO: {speech_pct, silence_pct, window}
  - BACKGROUND_SPEECH: {confidence, timestamp}
  - MULTIPLE_VOICES: {speaker_count, confidence, timestamp}
  - NOISE_SPIKE: {decibel_level, duration, timestamp}

- **Audio Preprocessing**
  - Noise reduction (spectral subtraction)
  - Audio normalization (dB level standardization)
  - 1-2 second rolling window buffering

- **Database Integration**
  - MongoDB for event storage
  - Audio statistics tracking
  - Exam-based event logging

## Installation

### Prerequisites

- Python 3.9+
- MongoDB (optional, for event persistence)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or use setup.py
python setup.py install
```

## Configuration

Configuration is managed through `src/config.py`. Key settings:

```python
# Audio Configuration
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 32
FRAME_SIZE = 512

# VAD Configuration
VAD_THRESHOLD = 0.5
VAD_MAX_LATENCY_MS = 100

# Voice Detection Configuration
BACKGROUND_SPEECH_THRESHOLD = 0.4
MULTIPLE_VOICES_THRESHOLD = 0.6
VOICE_DETECTION_WINDOW_MS = 5000  # 5 seconds

# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB = "audio_pipeline"
```

## Usage

### Starting the Server

```bash
python main.py --host 0.0.0.0 --port 5000 --debug
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Analyze Audio Chunk
```bash
POST /exams/{exam_id}/analyze-audio

# Request body: WAV audio file (16 kHz, mono)
# or JSON with base64 encoded audio: {"audio_base64": "..."}

# Response:
{
  "exam_id": "exam_123",
  "vad_score": 0.75,
  "background_speech_detected": false,
  "background_speech_confidence": 0.2,
  "multiple_voices_detected": false,
  "speaker_count": 1,
  "multiple_voices_confidence": 0.1,
  "events": [
    {
      "event_type": "VAD_DETECTED",
      "data": {"confidence": 0.75},
      "timestamp": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

#### Analyze Buffer
```bash
GET /exams/{exam_id}/analyze-buffer

# Response:
{
  "exam_id": "exam_123",
  "buffer_duration_s": 2.0,
  "speech_percentage": 65.5,
  "silence_percentage": 34.5,
  "speech_timestamps": [
    {"start": 0, "end": 1500},
    {"start": 1800, "end": 3200}
  ],
  "temporal_analysis": {
    "has_multiple_voices": false,
    "confidence": 0.1,
    "duration_s": 2.0,
    "voice_transitions": 2
  }
}
```

#### Get Statistics
```bash
GET /exams/{exam_id}/statistics

# Response:
{
  "exam_id": "exam_123",
  "statistics": {
    "total_frames": 100,
    "vad_frames": 75,
    "speech_percentage": 75.0,
    "avg_vad_score": 0.65,
    "max_vad_score": 0.95,
    "min_vad_score": 0.1,
    "background_speech_events": 2,
    "multiple_voices_events": 1,
    "buffer_duration_s": 3.2
  }
}
```

#### Get Events
```bash
GET /exams/{exam_id}/events?event_type=VAD_DETECTED&limit=50

# Response:
{
  "exam_id": "exam_123",
  "event_type_filter": "VAD_DETECTED",
  "events": [...],
  "count": 25
}
```

#### Reset Analysis
```bash
POST /exams/{exam_id}/reset

# Clears buffers and statistics for the exam
```

#### Shutdown Analysis
```bash
POST /exams/{exam_id}/shutdown

# Saves statistics, closes connections, and cleans up resources
```

## Python API

### Basic Usage

```python
import numpy as np
from src.audio_pipeline import AudioAnalysisPipeline
from scipy.io.wavfile import read

# Initialize pipeline
pipeline = AudioAnalysisPipeline(exam_id="exam_123")

# Read audio file
sample_rate, audio_data = read("audio.wav")

# Process audio chunks (assume 16 kHz)
chunk_size = 512  # 32ms at 16 kHz
for i in range(0, len(audio_data), chunk_size):
    chunk = audio_data[i:i+chunk_size]
    result = pipeline.process_audio_chunk(chunk)
    
    print(f"VAD Score: {result['vad_score']}")
    print(f"Background Speech: {result['background_speech_detected']}")
    print(f"Multiple Voices: {result['multiple_voices_detected']}")

# Analyze buffer
buffer_analysis = pipeline.analyze_buffer()
print(f"Speech: {buffer_analysis['speech_percentage']}%")
print(f"Silence: {buffer_analysis['silence_percentage']}%")

# Log to database
pipeline.log_events_to_db()
pipeline.log_statistics_to_db()

# Cleanup
pipeline.shutdown()
```

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_vad.py

# Specific test
pytest tests/test_vad.py::TestVoiceActivityDetector::test_vad_silence_detection
```

### Test Coverage

- Unit tests for VAD detection
- Preprocessing pipeline tests
- Voice detector tests
- Audio pipeline integration tests
- API endpoint tests

Target coverage: ≥80%

## Architecture

### Components

1. **VoiceActivityDetector** (`vad.py`)
   - Silero VAD model integration
   - Real-time speech detection

2. **AudioPreprocessor** (`preprocessing.py`)
   - Noise reduction
   - Audio normalization
   - Feature extraction (MFCC, spectral)

3. **VoiceDetector** (`voice_detector.py`)
   - Background speech detection
   - Multiple voices detection
   - Temporal pattern analysis

4. **AudioBuffer** (`audio_buffer.py`)
   - Rolling window buffer management

5. **AudioEventManager** (`audio_events.py`)
   - Event creation and aggregation

6. **MongoDBManager** (`database.py`)
   - Event persistence
   - Statistics logging

7. **AudioAnalysisPipeline** (`audio_pipeline.py`)
   - End-to-end audio processing
   - Result aggregation

8. **Flask API** (`api.py`)
   - RESTful endpoints
   - Request/response handling

## Performance

- **Latency**: <100ms per frame
- **CPU Usage**: Minimal (optimized for real-time)
- **Memory**: ~500MB for model + buffer
- **Throughput**: 16 kHz @ 32ms frames = 31.25 fps

## Security

- Audio is processed server-side
- No audio is stored on disk (events only)
- Encrypted audio transit (recommend HTTPS/TLS)
- Candidate consent required before processing

## Privacy

- Audio processing respects candidate privacy
- No unauthorized recording
- Event-based logging (not audio storage)
- GDPR compliant data handling

## Limitations (Phase-1)

- Basic voice separation (advanced diarization in Phase-2)
- No speaker identification
- Maximum 4 speaker detection
- Requires 16 kHz mono audio

## Future Enhancements (Phase-2)

- Advanced speaker diarization
- Speaker identification
- Real-time transcription
- Emotion detection
- Background noise classification

## License

[Specify your license]

## Support

For issues, please open a GitHub issue or contact support.

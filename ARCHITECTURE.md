# Architecture Documentation

## System Overview

The Audio VAD Pipeline is a modular, event-driven system for real-time audio analysis. It processes audio streams to detect voice activity, background speech, and multiple speakers.

## Module Structure

```
audio-vad-pipeline/
├── src/                          # Main application code
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── vad.py                   # Voice Activity Detection (Silero VAD)
│   ├── preprocessing.py          # Audio preprocessing (noise reduction, normalization)
│   ├── voice_detector.py         # Background speech & multiple voice detection
│   ├── audio_buffer.py           # Rolling window buffer management
│   ├── audio_events.py           # Event creation and management
│   ├── database.py               # MongoDB integration
│   ├── audio_pipeline.py         # Main orchestration pipeline
│   └── api.py                    # Flask REST API
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_vad.py              # VAD tests
│   ├── test_preprocessing.py    # Preprocessing tests
│   ├── test_voice_detector.py   # Voice detection tests
│   ├── test_audio_pipeline.py   # Pipeline tests
│   ├── test_api.py              # API endpoint tests
│   └── test_integration.py      # Integration tests
├── examples/                     # Example usage
│   ├── basic_usage.py           # Python API usage example
│   └── api_usage.py             # REST API usage example
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── pytest.ini                    # Pytest configuration
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose orchestration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # User documentation
└── ARCHITECTURE.md              # This file
```

## Component Details

### 1. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Key Parameters**:
- Audio: Sample rate (16 kHz), frame duration (32ms)
- VAD: Threshold (0.5), max latency (100ms)
- Voice Detection: Background speech threshold, multiple voices threshold
- Database: MongoDB connection string, collections
- Flask: Host, port, debug mode

### 2. Voice Activity Detection (`vad.py`)

**Purpose**: Real-time speech presence detection using Silero VAD

**Key Classes**:
- `VoiceActivityDetector`: Silero VAD wrapper

**Key Methods**:
- `detect_voice_activity()`: Returns VAD score (0-1) for audio chunk
- `get_speech_timestamps()`: Returns speech segment ranges in full audio

**Dependencies**: PyTorch, Silero VAD library

### 3. Audio Preprocessing (`preprocessing.py`)

**Purpose**: Audio cleanup and feature extraction

**Key Classes**:
- `AudioPreprocessor`: Preprocessing pipeline

**Key Methods**:
- `preprocess()`: Full preprocessing pipeline
- `_reduce_noise()`: High-pass filtering for noise removal
- `_normalize()`: Amplitude normalization to [-1, 1]
- `extract_mfcc_features()`: MFCC extraction for acoustic analysis
- `extract_spectral_features()`: Spectral characteristics (centroid, rolloff, energy, ZCR)
- `get_rms_energy()`: RMS energy calculation
- `audio_to_db()`: Amplitude to decibel conversion

**Dependencies**: librosa, scipy, NumPy

### 4. Voice Detector (`voice_detector.py`)

**Purpose**: Background speech and multiple voice detection

**Key Classes**:
- `VoiceDetector`: Voice pattern analysis

**Key Methods**:
- `detect_background_speech()`: Returns (detected: bool, confidence: float)
- `detect_multiple_voices()`: Returns (detected: bool, speaker_count: int, confidence: float)
- `analyze_temporal_patterns()`: Analyzes voice transitions over time window

**Detection Strategy**:
- Background speech: Uses spectral analysis and energy levels
- Multiple voices: Energy variance over time window + spectral characteristics
- Temporal tracking: Voice transition counting

### 5. Audio Buffer (`audio_buffer.py`)

**Purpose**: Rolling window buffer management

**Key Classes**:
- `AudioBuffer`: Circular buffer for time-windowed analysis

**Key Methods**:
- `add_audio()`: Add samples to buffer
- `get_buffer()`: Get current buffer contents
- `get_buffer_duration_s()`: Get buffer duration in seconds
- `is_full()`: Check if buffer is full

**Features**:
- Configurable duration (default 2 seconds)
- Circular/rolling buffer (maxlen-based)
- Automatic overflow handling

### 6. Audio Events (`audio_events.py`)

**Purpose**: Event creation and management

**Key Classes**:
- `AudioEvent`: Individual event representation
- `AudioEventManager`: Event aggregation

**Event Types**:
- VAD_DETECTED: Voice activity detected
- SPEECH_SILENCE_RATIO: Ratio of speech to silence
- BACKGROUND_SPEECH: Non-candidate voice detected
- MULTIPLE_VOICES: Multiple speakers detected
- NOISE_SPIKE: Sudden noise increase

**Key Methods**:
- `create_*_event()`: Event factory methods
- `get_events()`: Retrieve all events as dictionaries
- `get_events_by_type()`: Filter events by type

### 7. Database Integration (`database.py`)

**Purpose**: MongoDB persistence

**Key Classes**:
- `MongoDBManager`: MongoDB operations

**Collections**:
- `audio_events`: Event storage
- `audio_statistics`: Statistical snapshots

**Key Methods**:
- `insert_event()`: Store event in database
- `insert_statistics()`: Store statistics snapshot
- `get_events()`: Retrieve events with optional filtering
- `get_statistics()`: Get latest statistics for exam

**Features**:
- Graceful degradation if MongoDB unavailable
- Exam-based organization
- Timestamp tracking

### 8. Audio Pipeline (`audio_pipeline.py`)

**Purpose**: Main orchestration and workflow

**Key Classes**:
- `AudioAnalysisPipeline`: Complete analysis pipeline

**Key Methods**:
- `process_audio_chunk()`: Main processing function
- `analyze_buffer()`: Detailed buffer analysis
- `_calculate_statistics()`: Statistics aggregation
- `log_events_to_db()`: Persist events
- `log_statistics_to_db()`: Persist statistics
- `reset()`: Clear pipeline state
- `shutdown()`: Cleanup and close connections

**Workflow**:
1. Preprocess audio
2. Run VAD detection
3. Detect background speech
4. Detect multiple voices
5. Aggregate results and events
6. Update statistics
7. Optional: Log to database

### 9. Flask API (`api.py`)

**Purpose**: RESTful API endpoints

**Key Endpoints**:
- `GET /health`: Health check
- `POST /exams/{exam_id}/analyze-audio`: Process audio chunk
- `GET /exams/{exam_id}/analyze-buffer`: Buffer analysis
- `GET /exams/{exam_id}/statistics`: Get statistics
- `GET /exams/{exam_id}/events`: Get events
- `POST /exams/{exam_id}/reset`: Reset pipeline
- `POST /exams/{exam_id}/shutdown`: Shutdown and cleanup

**Features**:
- WAV audio format support
- Base64 JSON audio support
- CORS enabled
- Error handling and validation

## Data Flow

```
Audio Input
    ↓
Preprocessing (noise reduction, normalization)
    ↓
Buffering (rolling window)
    ↓
Parallel Detection:
  ├→ VAD Detection (Silero)
  ├→ Background Speech Detection
  └→ Multiple Voices Detection
    ↓
Event Generation
    ↓
Statistics Update
    ↓
Optional: Database Logging
    ↓
API Response
```

## Processing Pipeline

```
Raw Audio Chunk (PCM 16-bit, 16kHz, Mono)
         ↓
[AudioPreprocessor]
  - Noise Reduction (High-pass filter)
  - Normalization ([-1, 1] range)
         ↓
[Buffering]
  - Add to AudioBuffer
  - Maintain 2-second rolling window
         ↓
[Parallel Analysis]
  ├→ [VAD Detection]
  │   - Silero model inference
  │   - Return score 0-1
  │
  ├→ [Background Speech]
  │   - Spectral feature extraction
  │   - Energy calculation
  │   - Confidence scoring
  │
  └→ [Multiple Voices]
      - Energy variance calculation
      - Speaker count estimation
      - Confidence scoring
         ↓
[Event Generation]
  - Create appropriate events
  - Add to EventManager
         ↓
[Statistics Update]
  - Frame counts
  - Speech/silence ratio
  - VAD score aggregation
         ↓
[Result Aggregation]
  - Combine all detection results
  - Include events
  - Include updated statistics
         ↓
Response
```

## Configuration Hierarchy

1. **Default values** in `config.py`
2. **Environment variables** (if set)
3. **.env file** (via python-dotenv)
4. **Runtime parameters** (method arguments)

## Testing Strategy

### Unit Tests
- Individual component testing
- Mocked dependencies
- Input validation
- Output verification

### Integration Tests
- Full pipeline workflows
- Multiple concurrent pipelines
- Buffer management
- Statistics accuracy
- Event accumulation

### API Tests
- Endpoint functionality
- Request/response validation
- Error handling
- Content type negotiation

### Test Coverage Target
- Minimum 80% coverage
- Focus on critical paths
- Mock external dependencies (MongoDB)

## Performance Characteristics

### Latency
- Per-frame processing: <32ms (real-time at 16kHz)
- VAD inference: ~10ms
- Preprocessing: ~5ms
- Total per frame: <50ms

### Memory
- Model size: ~100MB (Silero VAD)
- Buffer size: ~64KB (2 seconds @ 16kHz)
- Total estimated: ~200MB with overhead

### CPU
- Single core capable
- Vectorized operations (NumPy)
- PyTorch CPU optimization

## Deployment

### Docker
- Containerized application
- MongoDB integration in docker-compose
- Health checks
- Automatic restart

### Configuration
- Environment-based configuration
- MongoDB connection pooling
- Graceful degradation

### Monitoring
- Health check endpoint
- Error logging
- Statistics tracking
- Event persistence

## Future Enhancements

### Phase 2
- Advanced speaker diarization
- Speaker identification
- Real-time transcription integration
- Emotion detection

### Phase 3
- Multi-language support
- Custom VAD models
- Advanced noise classification
- Real-time visualization

## Security Considerations

1. **Audio Privacy**
   - Server-side processing only
   - No disk storage (events only)
   - Temporary in-memory buffering

2. **Authentication**
   - Exam ID-based access control
   - TLS/HTTPS recommended
   - API key support (future)

3. **Data Protection**
   - MongoDB authentication
   - Event encryption support (future)
   - Audit logging (future)

## Dependencies

### Core
- PyTorch (ML inference)
- Silero VAD (speech detection)
- librosa (audio processing)
- NumPy (numerical computing)
- SciPy (signal processing)

### Web
- Flask (web framework)
- Flask-CORS (CORS support)

### Database
- PyMongo (MongoDB driver)

### Testing
- pytest (test framework)
- pytest-cov (coverage reporting)
- pytest-mock (mocking)

### Development
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

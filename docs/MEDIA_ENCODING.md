# Media Encoding Specifications

This document outlines the media encoding specifications for video and audio streaming in the online exam proctoring system.

## Video Encoding

### Format

- **Container**: None (individual frames)
- **Codec**: JPEG (browser native encoding)
- **Color Space**: RGB
- **Transport**: Base64-encoded data URL

### Quality Levels

#### Low Quality
- **Resolution**: 320x240 (ideal), max 640x480
- **Frame Rate**: 5 FPS
- **JPEG Quality**: 60%
- **Estimated Bandwidth**: ~50-100 kbps
- **Use Case**: Poor network conditions, multiple candidates

#### Medium Quality (Default)
- **Resolution**: 640x480 (ideal), max 1280x720
- **Frame Rate**: 10 FPS
- **JPEG Quality**: 80%
- **Estimated Bandwidth**: ~150-300 kbps
- **Use Case**: Standard monitoring

#### High Quality
- **Resolution**: 1280x720 (ideal), max 1920x1080
- **Frame Rate**: 15 FPS
- **JPEG Quality**: 90%
- **Estimated Bandwidth**: ~500-800 kbps
- **Use Case**: Detailed examination, small number of candidates

### Frame Capture Process

```javascript
// 1. Capture video frame from HTMLVideoElement
const canvas = document.createElement('canvas');
canvas.width = videoElement.videoWidth;
canvas.height = videoElement.videoHeight;

const ctx = canvas.getContext('2d');
ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

// 2. Encode as JPEG with quality setting
const frameData = canvas.toDataURL('image/jpeg', 0.8); // 80% quality

// 3. Send to server
websocket.send({
  type: 'video_frame',
  data: {
    frame_data: frameData,
    frame_number: frameNum,
    quality: 'medium'
  }
});
```

### Frame Rate Configuration

Frame rates are configurable based on network conditions:

| Network Quality | Recommended FPS | Max FPS |
|----------------|----------------|---------|
| Excellent (>1000 kbps) | 15 | 20 |
| Good (500-1000 kbps) | 10 | 15 |
| Fair (200-500 kbps) | 5 | 10 |
| Poor (<200 kbps) | 3 | 5 |

### Adaptive Quality

The system can automatically adjust quality based on network conditions:

```javascript
function adjustQuality(bandwidthKbps) {
  if (bandwidthKbps > 1000) {
    return { quality: 'high', fps: 15 };
  } else if (bandwidthKbps > 500) {
    return { quality: 'medium', fps: 10 };
  } else {
    return { quality: 'low', fps: 5 };
  }
}
```

## Audio Encoding

### Format

- **Codec**: Browser native (typically Opus or AAC)
- **Sample Rate**: 48000 Hz (default)
- **Channels**: Mono (1 channel)
- **Bit Rate**: Variable (16-32 kbps)

### Audio Processing

Audio is captured with the following constraints:

```javascript
const audioConstraints = {
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
  sampleRate: 48000,
  channelCount: 1
};
```

### Audio Features

#### Echo Cancellation
Removes echo from the audio stream to improve clarity.

#### Noise Suppression
Reduces background noise for better audio quality.

#### Auto Gain Control
Automatically adjusts microphone sensitivity to maintain consistent volume.

### Audio Chunk Size

Audio is sent in chunks to balance latency and efficiency:

- **Chunk Duration**: 1 second
- **Chunk Size**: ~6-12 KB (depending on codec)
- **Buffer Size**: 4096 samples

## WebRTC Constraints

### Video Constraints

```javascript
{
  video: {
    width: { ideal: 640, max: 1280 },
    height: { ideal: 480, max: 720 },
    frameRate: { ideal: 10, max: 15 },
    facingMode: 'user', // Front camera
    aspectRatio: 4/3
  }
}
```

### Audio Constraints

```javascript
{
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 48000,
    channelCount: 1
  }
}
```

## Bandwidth Optimization

### Frame Skipping

If bandwidth is insufficient, frames can be skipped:

```javascript
let frameCounter = 0;
const skipRate = 2; // Send every 2nd frame

if (frameCounter % skipRate === 0) {
  sendVideoFrame(capturedFrame);
}
frameCounter++;
```

### Quality Degradation

Automatically reduce quality when bandwidth drops:

```javascript
function handleBandwidthChange(newBandwidth) {
  if (newBandwidth < currentBandwidth * 0.7) {
    // Bandwidth dropped significantly
    decreaseQuality();
  } else if (newBandwidth > currentBandwidth * 1.3) {
    // Bandwidth improved
    increaseQuality();
  }
}
```

### Data Compression

Video frames are compressed using JPEG encoding. For further optimization:

1. **Reduce resolution**: Lower pixel dimensions
2. **Decrease quality**: Lower JPEG quality factor
3. **Reduce frame rate**: Send fewer frames per second
4. **Region of Interest**: Crop to face area only (future enhancement)

## Data Format Examples

### Video Frame Data URL

```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/...
```

### Base64 Encoding Size

For a 640x480 JPEG image at 80% quality:
- **Original size**: ~30-50 KB
- **Base64 encoded**: ~40-67 KB (33% increase)
- **Per frame**: 40-67 KB
- **At 10 FPS**: 400-670 KB/s (3.2-5.4 Mbps)

## Performance Considerations

### Client-Side

1. **Canvas Reuse**: Reuse the same canvas element for frame capture
2. **Throttling**: Limit frame capture to configured FPS
3. **Memory Management**: Clear canvas after each capture
4. **Worker Threads**: Use Web Workers for encoding (future enhancement)

### Server-Side

1. **Binary Transfer**: Consider using binary WebSocket frames for efficiency
2. **Frame Buffering**: Buffer frames for smooth playback
3. **Selective Broadcasting**: Only send frames to active invigilators
4. **Frame Dropping**: Drop old frames if buffer is full

## Browser Compatibility

### Video Capture

| Browser | Minimum Version | JPEG Quality | Notes |
|---------|----------------|--------------|-------|
| Chrome | 74+ | ✓ | Full support |
| Firefox | 66+ | ✓ | Full support |
| Safari | 12+ | ✓ | Requires HTTPS |
| Edge | 79+ | ✓ | Full support |

### Audio Capture

| Browser | Minimum Version | Audio Processing | Notes |
|---------|----------------|------------------|-------|
| Chrome | 74+ | ✓ | Full support |
| Firefox | 66+ | ✓ | Full support |
| Safari | 12+ | Partial | Limited processing |
| Edge | 79+ | ✓ | Full support |

## Testing Recommendations

### Frame Rate Testing

```javascript
let frameCount = 0;
let startTime = Date.now();

setInterval(() => {
  const elapsed = (Date.now() - startTime) / 1000;
  const actualFPS = frameCount / elapsed;
  console.log(`Actual FPS: ${actualFPS.toFixed(2)}`);
}, 5000);
```

### Bandwidth Monitoring

```javascript
let totalBytesSent = 0;
let lastCheck = Date.now();

function trackBandwidth(frameSize) {
  totalBytesSent += frameSize;
  
  const now = Date.now();
  if (now - lastCheck >= 5000) {
    const kbps = (totalBytesSent * 8) / (now - lastCheck);
    console.log(`Bandwidth: ${kbps.toFixed(2)} kbps`);
    totalBytesSent = 0;
    lastCheck = now;
  }
}
```

### Quality Assessment

Monitor these metrics:
- Frame rate stability
- Frame drop rate
- Encoding time per frame
- Network latency
- Buffer utilization

## Future Enhancements

1. **H.264 Hardware Encoding**: Use native browser support for H.264 encoding
2. **WebCodecs API**: Leverage WebCodecs for efficient encoding
3. **VP8/VP9 Support**: Alternative codec support
4. **Adaptive Bitrate**: Dynamic quality adjustment
5. **Face Detection**: Crop frames to face region
6. **Delta Frames**: Send only changed regions
7. **Binary Protocol**: Use binary WebSocket frames instead of base64

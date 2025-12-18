# Quick Start Guide

This guide will help you get the online exam proctoring system up and running in minutes.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn
- A modern browser (Chrome 90+, Firefox 80+, or Edge 90+ recommended)

## Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
cd /path/to/project

# Verify the structure
ls -la
# Should see: backend/, frontend/, docs/, README.md
```

## Step 2: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open!**

## Step 3: Start the Frontend

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
```

**Keep this terminal open too!**

## Step 4: Test the System

### Test as a Candidate

1. Open your browser and go to: http://localhost:3000
2. Click **"Try Demo Session"**
3. You'll see the consent banner - click **"Accept & Continue"**
4. When the browser asks for camera/microphone permissions, click **"Allow"**
5. You should see:
   - Your video preview
   - Audio level visualization
   - Connection status showing "Connected"
   - Session information

### Test as an Invigilator

1. Open a **new browser tab** or window
2. Go to: http://localhost:3000/invigilator/exam-001?invigilator_id=inv-123
3. You should see:
   - "Active Candidates" section
   - Your candidate session from the previous tab should appear
   - Video feed from the candidate
   - Connection status

### Verify Real-Time Communication

1. In the candidate tab, move around in front of the camera
2. In the invigilator tab, you should see the video update in real-time
3. In the candidate tab, speak into the microphone
4. Watch the audio level indicator respond to your voice

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Make sure you activated the virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Then reinstall
pip install -r requirements.txt
```

**Problem:** Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Then update frontend .env.local:
# NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

### Frontend Issues

**Problem:** `Module not found` errors
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Port 3000 already in use
```bash
# Next.js will automatically use the next available port (3001, 3002, etc.)
# Just note the port number shown in the terminal
```

### Browser Issues

**Problem:** Camera/microphone not working
- Ensure you're using a supported browser (Chrome 90+, Firefox 80+, Edge 90+)
- Check browser permissions (should see camera icon in address bar)
- Try using `http://localhost:3000` instead of `http://127.0.0.1:3000`
- On Safari, you must use HTTPS (localhost won't work)

**Problem:** WebSocket connection fails
- Ensure backend is running on port 8000
- Check browser console for errors (F12 → Console tab)
- Verify firewall isn't blocking WebSocket connections

**Problem:** "HTTPS required" error
- For development, use Chrome, Firefox, or Edge (they allow localhost)
- Safari requires HTTPS even on localhost
- For production, use proper HTTPS certificates

## Testing Multiple Candidates

To test with multiple candidates:

1. Open multiple browser tabs/windows
2. For each candidate, use a different session ID:
   - `http://localhost:3000/candidate/session-001?exam_id=exam-001`
   - `http://localhost:3000/candidate/session-002?exam_id=exam-001`
   - `http://localhost:3000/candidate/session-003?exam_id=exam-001`
3. Open invigilator view: `http://localhost:3000/invigilator/exam-001?invigilator_id=inv-123`
4. You should see all candidates in the invigilator dashboard

## Next Steps

### Configure Video Quality

Edit the candidate page to adjust quality:

```typescript
<MediaCapture
  sessionId={sessionId}
  examId={examId}
  videoQuality="high"  // Change to 'low', 'medium', or 'high'
  fps={15}             // Change frame rate (5-20)
  // ...
/>
```

### Set Up Production Environment

1. Get SSL certificates for HTTPS
2. Configure environment variables:
   ```bash
   # Backend .env
   CORS_ORIGINS=https://your-frontend-domain.com
   
   # Frontend .env.local
   NEXT_PUBLIC_WS_URL=wss://your-backend-domain.com
   ```
3. Build and deploy:
   ```bash
   # Backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   
   # Frontend
   npm run build
   npm start
   ```

## API Endpoints

### REST Endpoints
- `GET http://localhost:8000/` - API info
- `GET http://localhost:8000/health` - Health check
- `GET http://localhost:8000/stats` - Connection statistics

### WebSocket Endpoints
- `WS ws://localhost:8000/ws/exam/{exam_id}?invigilator_id={id}` - Invigilator
- `WS ws://localhost:8000/ws/candidate/{session_id}?exam_id={id}` - Candidate

## Documentation

For more detailed information, see:
- [README.md](README.md) - Full project documentation
- [docs/WEBSOCKET_PROTOCOL.md](docs/WEBSOCKET_PROTOCOL.md) - Message protocol
- [docs/MEDIA_ENCODING.md](docs/MEDIA_ENCODING.md) - Video/audio encoding
- [docs/BROWSER_COMPATIBILITY.md](docs/BROWSER_COMPATIBILITY.md) - Browser support

## Need Help?

1. Check the browser console (F12) for errors
2. Check backend logs in the terminal
3. Review the documentation in the `docs/` directory
4. Ensure all prerequisites are met
5. Try with the recommended browsers first

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4 GB
- Network: 1 Mbps upload (per candidate)
- Browser: Chrome 74+, Firefox 66+, Edge 79+

### Recommended
- CPU: 4 cores
- RAM: 8 GB
- Network: 5 Mbps upload (per candidate)
- Browser: Chrome 90+, Firefox 80+, Edge 90+

---

**Happy Testing!** 🚀

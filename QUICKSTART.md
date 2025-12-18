# Quick Start Guide

Get the Exam Activity Monitoring System up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- OR Node.js 18+, Python 3.11+, and MongoDB 7.0

## Option 1: Docker Compose (Recommended) ⚡

The fastest way to get started:

```bash
# 1. Clone the repository
git clone <repository-url>
cd exam-monitoring

# 2. Start all services
docker-compose up -d

# 3. Wait for services to start (about 30 seconds)
docker-compose logs -f

# 4. Open your browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

That's it! The system is now running.

### Test the System

1. Navigate to http://localhost:3000
2. Click "Start Demo Exam"
3. Accept the consent banner
4. Try these actions:
   - Switch tabs (Alt+Tab or Cmd+Tab)
   - Copy text (Ctrl+C or Cmd+C)
   - Try to paste (Ctrl+V or Cmd+V) - should be blocked
   - Stay idle for 30+ seconds

5. View logged events:
   ```bash
   # Get events for your session
   curl http://localhost:8000/api/events/session/<session-id>
   ```

### Stop the System

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

## Option 2: Manual Setup 🛠️

### Step 1: Start MongoDB

```bash
docker run -d -p 27017:27017 --name exam-mongodb mongo:7.0
```

### Step 2: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URL="mongodb://localhost:27017"
export DATABASE_NAME="exam_monitoring"

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Step 3: Setup Frontend

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws" > .env.local

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Step 4: Test the System

Follow the same testing steps as Docker Compose above.

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 3000
lsof -i :3000

# Check what's using port 8000
lsof -i :8000

# Check what's using port 27017
lsof -i :27017

# Kill the process if needed
kill -9 <PID>
```

### MongoDB Connection Failed

```bash
# Check if MongoDB is running
docker ps | grep mongo

# View MongoDB logs
docker logs exam-mongodb

# Restart MongoDB
docker restart exam-mongodb
```

### WebSocket Connection Failed

1. Check backend is running: http://localhost:8000/health
2. Check browser console for errors
3. Verify CORS settings in `backend/app/config.py`
4. Ensure WebSocket URL is correct in frontend `.env.local`

### Frontend Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev
```

## Next Steps

### Customize Configuration

Edit these files to customize the system:

**Backend Configuration** (`backend/app/config.py`):
```python
class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "exam_monitoring"
    cors_origins: list = ["http://localhost:3000"]
    # Add your custom settings
```

**Frontend Configuration** (`frontend/.env.local`):
```env
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
# Add your custom environment variables
```

### Modify Monitoring Behavior

**Change Inactivity Threshold** (default: 30 seconds):

Edit `frontend/src/pages/exam.tsx`:
```typescript
const config: MonitoringConfig = {
  // ...
  inactivityThreshold: 60000, // 60 seconds
};
```

**Enable/Disable Paste Blocking**:

```typescript
const config: MonitoringConfig = {
  // ...
  disablePaste: false, // Allow paste
};
```

### Run Tests

**Frontend Tests**:
```bash
cd frontend
npm test
npm test -- --coverage
```

**Backend Tests**:
```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

### Production Deployment

For production deployment:

1. **Environment Variables**:
   ```bash
   # Backend
   export MONGODB_URL="mongodb://production-host:27017"
   export CORS_ORIGINS='["https://your-domain.com"]'
   
   # Frontend
   export NEXT_PUBLIC_WS_URL="wss://your-domain.com/ws"
   ```

2. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   npm start
   ```

3. **Run Backend with Production Server**:
   ```bash
   cd backend
   gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

4. **Use HTTPS/WSS**:
   - Set up SSL/TLS certificates
   - Use `wss://` instead of `ws://` for WebSocket
   - Configure reverse proxy (nginx, traefik, etc.)

5. **Security Considerations**:
   - Enable authentication
   - Set up rate limiting
   - Configure firewall rules
   - Enable MongoDB authentication
   - Use environment-specific secrets

## Common Use Cases

### 1. Testing Tab Switching Detection

```bash
# Start the exam
# Open a new tab
# Switch between tabs
# Check backend logs to see events
docker-compose logs backend | grep TAB_SWITCHED
```

### 2. Testing Copy-Paste Detection

```bash
# Start the exam
# Select and copy text (Ctrl+C)
# Try to paste (Ctrl+V) - should be blocked
# Check backend logs
docker-compose logs backend | grep COPY_DETECTED
docker-compose logs backend | grep PASTE_DETECTED
```

### 3. Testing Inactivity Detection

```bash
# Start the exam
# Don't touch keyboard/mouse for 30+ seconds
# Check backend logs
docker-compose logs backend | grep INACTIVITY
```

### 4. Viewing Events in MongoDB

```bash
# Connect to MongoDB
docker exec -it exam_monitoring_mongodb mongosh

# Switch to database
use exam_monitoring

# View all events
db.monitoring_events.find().pretty()

# View events by type
db.monitoring_events.find({event_type: "TAB_SWITCHED"}).pretty()

# Count events by type
db.monitoring_events.aggregate([
  {$group: {_id: "$event_type", count: {$sum: 1}}}
])
```

## Integration Examples

### Integrate into Existing Exam Platform

**1. Install as dependency**:
```bash
npm install @your-org/exam-monitoring
```

**2. Import and use**:
```typescript
import { ActivityMonitor } from '@your-org/exam-monitoring';

function ExamPage() {
  const config = {
    sessionId: examSession.id,
    candidateId: student.id,
    inactivityThreshold: 30000,
    disablePaste: exam.blockPaste,
    websocketUrl: process.env.MONITORING_WS_URL,
  };
  
  return (
    <>
      <ActivityMonitor config={config} enabled={true} />
      {/* Your existing exam content */}
    </>
  );
}
```

### Custom Event Handler

```typescript
import { monitoringEventEmitter } from '@your-org/exam-monitoring';

monitoringEventEmitter.subscribe((event) => {
  // Custom handling
  console.log('Monitoring event:', event);
  
  // Send to your analytics
  analytics.track(event.type, event);
  
  // Show warning to user
  if (event.type === 'TAB_SWITCHED') {
    showWarning('Please stay on the exam tab');
  }
});
```

## Resources

- **Full Documentation**: See [README.md](README.md)
- **Privacy Policy**: See [PRIVACY.md](PRIVACY.md)
- **Contributing Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **API Documentation**: http://localhost:8000/docs (when running)

## Support

Need help? 
- Check the [README.md](README.md) for detailed documentation
- Open an issue on GitHub
- Review existing issues for solutions

## What's Next?

Once you have the system running:
1. ✅ Read the [Privacy Policy](PRIVACY.md)
2. ✅ Review [API Documentation](http://localhost:8000/docs)
3. ✅ Run the test suite
4. ✅ Customize for your use case
5. ✅ Read [Contributing Guide](CONTRIBUTING.md) if you want to contribute

Happy monitoring! 🎉

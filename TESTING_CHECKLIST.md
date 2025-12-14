# Testing Checklist

Use this checklist to verify all features are working correctly.

## Pre-Testing Setup

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Browser is Chrome 90+, Firefox 80+, or Edge 90+
- [ ] Camera and microphone are connected and working

## Backend Tests

### Health Checks
- [ ] Access `http://localhost:8000/` - Should return API information
- [ ] Access `http://localhost:8000/health` - Should return `{"status": "healthy"}`
- [ ] Access `http://localhost:8000/stats` - Should return connection statistics

### WebSocket Connection
- [ ] Backend logs show "Starting WebSocket ping task..."
- [ ] No errors in backend terminal

## Frontend Tests

### Home Page
- [ ] Access `http://localhost:3000/`
- [ ] Page loads without errors
- [ ] Two cards visible: "Candidate Portal" and "Invigilator Portal"
- [ ] Both demo links are clickable

### Candidate Flow - Permission Request

**Test URL:** `http://localhost:3000/candidate/test-session-001?exam_id=exam-test`

- [ ] Consent banner appears on page load
- [ ] Banner has "Accept & Continue" and "Decline" buttons
- [ ] "Show more details" expands privacy information
- [ ] Clicking "Decline" shows appropriate message
- [ ] Clicking "Accept & Continue" triggers browser permission prompt

### Candidate Flow - Permission Grant

- [ ] Click "Accept & Continue" on consent banner
- [ ] Browser shows permission prompt for camera and microphone
- [ ] Click "Allow" on browser prompt
- [ ] Video preview appears showing camera feed
- [ ] Video shows "Live" indicator in bottom-left corner
- [ ] Audio level visualizer appears
- [ ] Audio bars respond to microphone input (try speaking)
- [ ] Connection status shows "Connected" (green indicator)

### Candidate Flow - Video Controls

- [ ] "Disable Video" button works (video turns off)
- [ ] "Enable Video" button works (video turns on)
- [ ] "Mute Audio" button works (audio indicator stops)
- [ ] "Unmute Audio" button works (audio indicator resumes)

### Candidate Flow - Session Information

- [ ] Session ID is displayed correctly
- [ ] Exam ID is displayed correctly
- [ ] Video status shows "Active" when enabled
- [ ] Audio status shows "Active" when enabled
- [ ] Quality setting is displayed (medium by default)
- [ ] FPS is displayed (10 by default)
- [ ] Frame counter increments over time

### Invigilator Flow - Basic

**Test URL:** `http://localhost:3000/invigilator/exam-test?invigilator_id=inv-001`

- [ ] Page loads without errors
- [ ] Connection status appears in header
- [ ] "Active Candidates" section is visible
- [ ] "Alerts" panel is visible on the right

### Invigilator Flow - Monitoring

With candidate page still open in another tab:

- [ ] Candidate appears in "Active Candidates" list
- [ ] Candidate's video feed is visible
- [ ] Session ID matches the candidate
- [ ] Status shows "streaming"
- [ ] Video indicator shows "✓ Active"
- [ ] Audio indicator shows "✓ Active"

### Invigilator Flow - Real-Time Updates

In the candidate tab:
- [ ] Move in front of camera - invigilator view updates
- [ ] Wave your hand - movement appears in invigilator view
- [ ] Disable video - invigilator shows "✕ Inactive"
- [ ] Enable video - invigilator shows "✓ Active"

### Multi-Candidate Test

Open 3 candidate tabs with different session IDs:
1. `http://localhost:3000/candidate/session-001?exam_id=exam-test`
2. `http://localhost:3000/candidate/session-002?exam_id=exam-test`
3. `http://localhost:3000/candidate/session-003?exam_id=exam-test`

Grant permissions in all tabs.

In invigilator tab:
- [ ] All 3 candidates appear
- [ ] Each has their own video feed
- [ ] Each shows correct session ID
- [ ] All show "streaming" status

### Connection Tests

#### Reconnection Test
In candidate tab:
- [ ] Open browser DevTools (F12) → Network tab
- [ ] Filter by "WS" (WebSocket)
- [ ] Find the WebSocket connection
- [ ] Right-click and "Close connection"
- [ ] Connection status shows "Reconnecting..."
- [ ] Connection automatically reconnects
- [ ] Connection status shows "Connected" again
- [ ] Video streaming resumes

#### Page Refresh Test
- [ ] Refresh candidate page
- [ ] Consent banner appears again (expected behavior)
- [ ] Accept consent and grant permissions
- [ ] Video and audio resume
- [ ] Invigilator view updates with new connection

### Error Handling Tests

#### Permission Denied Test
1. Open new incognito/private window
2. Go to candidate page
3. Accept consent
4. Click "Block" when browser asks for permissions
   - [ ] Error message appears explaining the issue
   - [ ] Error is user-friendly
   - [ ] Invigilator receives alert about denied permissions

#### Device Not Found Test
Only if you can test without a camera:
- [ ] Appropriate error message appears
- [ ] Error explains no camera was found

### Browser Console Tests

In candidate tab, open DevTools (F12) → Console:
- [ ] No errors in red
- [ ] May see info messages about connections (acceptable)
- [ ] WebSocket messages can be seen (if logging enabled)

In invigilator tab, open DevTools (F12) → Console:
- [ ] No errors in red
- [ ] Connection messages appear
- [ ] Video frame messages appear when candidates are streaming

### Performance Tests

With 1 candidate connected:
- [ ] Video appears smooth (not choppy)
- [ ] Audio level indicator responds immediately
- [ ] No significant lag in invigilator view (< 1 second)
- [ ] Browser tab doesn't freeze or hang

With 3 candidates connected:
- [ ] All video feeds update
- [ ] No excessive lag
- [ ] CPU usage acceptable (check Task Manager/Activity Monitor)

### Network Tests

In browser DevTools → Network tab:
- [ ] WebSocket connection shows "101 Switching Protocols"
- [ ] WebSocket connection stays open (green indicator)
- [ ] Messages flow bidirectionally
- [ ] No failed requests

### Quality Settings Test

Modify candidate page to test different qualities:

**Low Quality:**
```typescript
<MediaCapture videoQuality="low" fps={5} />
```
- [ ] Video quality is noticeably lower
- [ ] Frame rate is slower
- [ ] Bandwidth usage reduced

**High Quality:**
```typescript
<MediaCapture videoQuality="high" fps={15} />
```
- [ ] Video quality is noticeably better
- [ ] Frame rate is faster
- [ ] Bandwidth usage increased

## Cross-Browser Tests

Repeat key tests in each browser:

### Chrome
- [ ] Candidate flow works
- [ ] Invigilator monitoring works
- [ ] Reconnection works
- [ ] Audio visualization works

### Firefox
- [ ] Candidate flow works
- [ ] Invigilator monitoring works
- [ ] Reconnection works
- [ ] Audio visualization works

### Edge
- [ ] Candidate flow works
- [ ] Invigilator monitoring works
- [ ] Reconnection works
- [ ] Audio visualization works

### Safari (if available)
- [ ] Must use HTTPS (skip localhost test)
- [ ] Audio processing may be limited
- [ ] Basic functionality works

## Production Readiness Tests

### HTTPS Test
If you have SSL certificates:
- [ ] Backend runs with HTTPS
- [ ] Frontend runs with HTTPS
- [ ] WebSocket uses WSS protocol
- [ ] All features work over HTTPS

### Environment Variables Test
- [ ] Backend respects CORS_ORIGINS
- [ ] Frontend respects NEXT_PUBLIC_WS_URL
- [ ] Configuration changes take effect

## Documentation Tests

- [ ] README.md is clear and accurate
- [ ] QUICKSTART.md instructions work
- [ ] WEBSOCKET_PROTOCOL.md matches implementation
- [ ] MEDIA_ENCODING.md is technically accurate
- [ ] BROWSER_COMPATIBILITY.md is up-to-date

## Final Verification

- [ ] All backend Python files compile without syntax errors
- [ ] All frontend TypeScript files compile without errors
- [ ] No TODO or FIXME comments in production code
- [ ] .gitignore includes necessary patterns
- [ ] No sensitive data in code
- [ ] No hardcoded credentials

## Test Results Summary

**Date Tested:** _______________  
**Tested By:** _______________  
**Browser:** _______________  
**OS:** _______________

**Overall Result:** ☐ Pass ☐ Fail

**Issues Found:**
1. _______________
2. _______________
3. _______________

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

---

## Quick Test Script

For rapid smoke testing:

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser:
# 1. Open http://localhost:3000/candidate/test?exam_id=exam
# 2. Accept consent and permissions
# 3. Open http://localhost:3000/invigilator/exam?invigilator_id=inv
# 4. Verify video appears
# 5. ✅ Pass if video streams successfully
```

---

**All Tests Passing?** → System is ready! 🎉

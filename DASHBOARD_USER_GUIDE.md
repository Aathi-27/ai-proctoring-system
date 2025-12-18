# Invigilator Dashboard User Guide

## Overview

The Invigilator Dashboard is a real-time exam monitoring system that provides live video feeds, risk assessment, and proctoring tools for managing candidate examinations.

## Dashboard Layout

### Header
- **Exam Name**: Displays the current exam title
- **Exam Status**: Shows start time and active candidate count
- **Connection Status**: Green indicator when connected to the server, red when disconnected
- **Keyboard Shortcuts**: Reference for Alt+P (Pause) and Alt+F (Flag)
- **Logout Button**: Securely end your session

### Left Sidebar - Active Sessions
Lists all currently active examination sessions with:
- **Candidate Name**: Full name of the candidate
- **Session ID**: Unique identifier for tracking
- **Risk Score Meter**: Circular gauge showing current risk assessment
  - **Green (<30%)**: Low risk - candidate appears compliant
  - **Yellow (30-60%)**: Medium risk - minor anomalies detected
  - **Orange (60-85%)**: High risk - significant concerns present
  - **Red (85-100%)**: Critical risk - immediate action recommended
- **Status Badges**: Visual indicators for paused or flagged sessions

### Center - Video Feeds
- **Main Video Feed**: Large HD stream of selected candidate
  - Candidate information overlay (name, ID, elapsed time)
  - Risk score meter in top-right corner
  - Status badge (if paused/flagged) in top-left corner
- **Additional Feeds**: 2-4 thumbnail feeds for quick candidate switching
- **Risk Trend Chart**: Shows risk score progression over the last 5 minutes

### Right Panel
#### Real-Time Alerts
- **Most Recent First**: Newest alerts appear at the top
- **Alert Types**: Color-coded by severity
  - Mobile phone detected
  - Face not visible
  - Multiple faces in frame
  - Copy/paste activity
  - Tab switching
  - Inactivity
  - Audio anomalies
  - Manual notes
- **Acknowledge Button**: Mark alerts as reviewed
- **Evidence Link**: Quick access to snapshot evidence

#### Event Timeline
- **Chronological Log**: All events from all sessions in time order
- **Expandable Details**: Click event to see:
  - Confidence percentage
  - Risk contribution score
  - Session information
  - Evidence snapshot
- **Severity Filter**: View only critical, high, or all events
- **Visual Indicators**: Color-coded timeline dots

### Bottom Panel - Evidence Gallery
- **Recent Snapshots**: Thumbnail gallery of captured evidence
- **Risk Score Display**: Current risk score at time of capture
- **Full View**: Click thumbnail to expand to full resolution
- **Metadata**: Timestamp, event type, and risk score details
- **Download**: Save evidence for post-exam review

## Key Features

### Real-Time Monitoring
- Live HD video feeds update within 2 seconds
- Risk scores recalculate as new events occur
- Alerts deliver within 500ms of backend detection

### Session Management

#### Pause Exam
1. Click on a candidate session in the left sidebar
2. Click the arrow icon to expand action buttons
3. Click "⏸️ Pause Exam" button
4. Session will show PAUSED status
5. Click again to resume

#### Flag Session
1. Click on a candidate session in the left sidebar
2. Click the arrow icon to expand action buttons
3. Click "🚩 Flag Session" button
4. Session will show FLAGGED status for post-exam review
5. Click again to unflag

### Alert Management

#### Acknowledge Alerts
1. Locate alert in the Real-Time Alerts panel
2. Review the alert details and any associated evidence
3. Click "Acknowledge" button
4. Alert will be marked as reviewed and styled differently

#### Filter Alerts
1. Use the filter buttons in the alert panel header
2. Select "All" to see all alerts
3. Click specific icons to filter by alert type
4. Low-priority alerts auto-dismiss after 30 seconds

#### View Evidence
1. Look for the "Evidence" button on any alert
2. Click to view the snapshot in a modal
3. View metadata including timestamp and confidence score
4. Download evidence for records

### Timeline Analysis

#### Expand Event Details
1. Click on any event in the Event Timeline
2. View:
   - Event confidence percentage
   - Risk contribution score
   - Session information
   - Timestamp and snapshot
3. Click again to collapse

#### Filter by Severity
1. Click filter buttons: "All", "Critical", or "High"
2. Timeline updates to show filtered events
3. Use to focus on high-priority events

### Video Management

#### Switch Candidate View
1. Click a candidate name in the left sidebar to select
2. Main video feed updates to show selected candidate
3. Or click a thumbnail in the video grid to switch

#### Interpret Video Overlay
- **Top-Right**: Current risk score meter
- **Top-Left**: Status badge (if applicable)
- **Bottom-Left**: Candidate information card
- **Bottom**: Risk trend chart

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Alt + P | Pause selected session |
| Alt + F | Flag selected session |
| Escape | Close modals/fullscreen evidence |

## Accessibility Features

- **High Contrast Mode**: Supported for visibility impairments
- **Keyboard Navigation**: All functions accessible via keyboard
- **Color-Coded Information**: Paired with text labels
- **WCAG 2.1 AA Compliance**: Full accessibility standard support

## Performance Notes

- Dashboard handles 10-50 concurrent candidates
- Video streams optimized for HD quality
- Automatic reconnection if server connection drops
- Client remains responsive even with high alert volume

## Troubleshooting

### Connection Lost
- Red indicator in header shows disconnected state
- Dashboard automatically attempts to reconnect
- Wait for green indicator to return
- Refresh page if reconnection fails

### Missing Video Feed
- Check connection status first
- Ensure candidate's camera is enabled
- Verify network bandwidth is sufficient
- Contact IT support if issue persists

### Alerts Not Updating
- Confirm WebSocket connection (green indicator)
- Try acknowledging and re-opening alert
- Refresh page as last resort
- Check with system administrator

## Best Practices

1. **Position Monitor**: Place at 90-degree angle for clear viewing
2. **Regular Breaks**: Take brief breaks during long exams
3. **Monitor All Feeds**: Check multiple candidates regularly
4. **Respond Quickly**: Act on critical alerts within seconds
5. **Document Issues**: Use flag function for suspicious behavior
6. **Keep Alerts Clear**: Acknowledge reviewed alerts regularly

## Support

For technical issues or questions:
- Contact your examination coordinator
- Report bugs to the IT support team
- Request feature enhancements through your system administrator

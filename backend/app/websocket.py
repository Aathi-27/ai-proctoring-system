from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import logging
from .database import db
from .models import (
    MonitoringEventType,
    MonitoringEventDocument,
    TabSwitchedEvent,
    ClipboardEvent,
    InactivityEvent,
    ActivityResumedEvent,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        if session_id:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected for session: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str = None):
        if session_id and session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected for session: {session_id}")

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")


manager = ConnectionManager()


async def handle_monitoring_event(event_data: dict) -> MonitoringEventDocument:
    event_type = event_data.get("type")
    
    doc_data = {
        "event_type": event_type,
        "timestamp": event_data.get("timestamp"),
        "session_id": event_data.get("sessionId"),
        "candidate_id": event_data.get("candidateId"),
    }
    
    if event_type == MonitoringEventType.TAB_SWITCHED:
        doc_data["inactive_duration"] = event_data.get("inactive_duration")
    
    elif event_type in [MonitoringEventType.COPY_DETECTED, MonitoringEventType.PASTE_DETECTED]:
        doc_data["content_length"] = event_data.get("content_length")
    
    elif event_type in [MonitoringEventType.KEYBOARD_INACTIVITY, MonitoringEventType.MOUSE_INACTIVITY]:
        doc_data["duration_seconds"] = event_data.get("duration_seconds")
    
    return MonitoringEventDocument(**doc_data)


async def websocket_endpoint(websocket: WebSocket, session_id: str = None):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                event_data = json.loads(data)
                logger.info(f"Received event: {event_data.get('type')} for session: {session_id}")
                
                event_doc = await handle_monitoring_event(event_data)
                
                await db.insert_event(event_doc.to_dict())
                
                await manager.send_message(
                    json.dumps({"status": "success", "event_type": event_data.get("type")}),
                    websocket
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await manager.send_message(
                    json.dumps({"status": "error", "message": "Invalid JSON"}),
                    websocket
                )
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                await manager.send_message(
                    json.dumps({"status": "error", "message": str(e)}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)

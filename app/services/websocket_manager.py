import json
import asyncio
import logging
from typing import Dict, Set, List, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.models.alerts import AlertEvent, InvigilatorConnection


logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time alert broadcasting"""
    
    def __init__(self):
        # exam_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # connection_id -> connection info
        self.connection_info: Dict[str, InvigilatorConnection] = {}
        # WebSocket -> connection_id mapping
        self.websocket_to_connection: Dict[WebSocket, str] = {}
        # Message queue for retry logic
        self.message_queue: Dict[str, List[AlertEvent]] = {}
        # Acknowledgment tracking
        self.message_id_counter = 0
        
    async def connect(self, websocket: WebSocket, exam_id: str, invigilator_id: str) -> str:
        """Establish WebSocket connection and register invigilator"""
        await websocket.accept()
        
        connection_id = f"{invigilator_id}_{datetime.utcnow().timestamp()}"
        
        # Create connection info
        connection_info = InvigilatorConnection(
            connection_id=connection_id,
            exam_id=exam_id,
            invigilator_id=invigilator_id
        )
        
        # Register connection
        if exam_id not in self.active_connections:
            self.active_connections[exam_id] = set()
        self.active_connections[exam_id].add(websocket)
        self.connection_info[connection_id] = connection_info
        self.websocket_to_connection[websocket] = connection_id
        
        logger.info(f"Invigilator {invigilator_id} connected to exam {exam_id}")
        
        # Send connection acknowledgment
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return connection_id
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and cleanup"""
        connection_id = self.websocket_to_connection.get(websocket)
        if connection_id:
            connection_info = self.connection_info.get(connection_id)
            if connection_info:
                exam_id = connection_info.exam_id
                invigilator_id = connection_info.invigilator_id
                
                # Remove from active connections
                if exam_id in self.active_connections:
                    self.active_connections[exam_id].discard(websocket)
                    if not self.active_connections[exam_id]:
                        del self.active_connections[exam_id]
                
                # Cleanup mappings
                del self.websocket_to_connection[websocket]
                if connection_id in self.connection_info:
                    del self.connection_info[connection_id]
                
                logger.info(f"Invigilator {invigilator_id} disconnected from exam {exam_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket connection"""
        try:
            # Add message ordering with timestamp and ID
            message["message_id"] = self._get_next_message_id()
            message["server_timestamp"] = datetime.utcnow().isoformat()
            
            await websocket.send_text(json.dumps(jsonable_encoder(message)))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            # Connection likely broken, cleanup
            self.disconnect(websocket)
    
    async def broadcast_alert(self, exam_id: str, alert: AlertEvent):
        """Broadcast alert to all connected invigilators for an exam"""
        logger.debug(f"Broadcasting alert for exam {exam_id}, active connections: {list(self.active_connections.keys())}")
        
        if exam_id not in self.active_connections:
            logger.warning(f"No active connections for exam {exam_id}")
            return
        
        message = {
            "type": "alert",
            "alert": jsonable_encoder(alert)
        }
        
        logger.debug(f"Broadcasting to {len(self.active_connections[exam_id])} connections")
        
        disconnected_connections = []
        
        # Send to all connected invigilators
        for websocket in self.active_connections[exam_id].copy():
            try:
                await self.send_personal_message(websocket, message)
                logger.debug("Alert sent to WebSocket successfully")
            except WebSocketDisconnect:
                logger.debug("WebSocket disconnected during broadcast")
                disconnected_connections.append(websocket)
            except Exception as e:
                logger.error(f"Failed to send alert to WebSocket: {e}")
                disconnected_connections.append(websocket)
        
        # Cleanup disconnected connections
        for websocket in disconnected_connections:
            self.disconnect(websocket)
    
    async def send_acknowledgment(self, websocket: WebSocket, alert_id: str, success: bool = True):
        """Send acknowledgment response to invigilator"""
        message = {
            "type": "acknowledgment",
            "alert_id": alert_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(websocket, message)
    
    def get_connected_invigilators(self, exam_id: str) -> List[InvigilatorConnection]:
        """Get list of connected invigilators for an exam"""
        if exam_id not in self.active_connections:
            return []
        
        invigilators = []
        for websocket in self.active_connections[exam_id]:
            connection_id = self.websocket_to_connection.get(websocket)
            if connection_id and connection_id in self.connection_info:
                invigilators.append(self.connection_info[connection_id])
        
        return invigilators
    
    async def handle_reconnection(self, websocket: WebSocket, exam_id: str, invigilator_id: str, 
                                last_message_id: Optional[str] = None):
        """Handle reconnection with message resumption"""
        # Close existing connection if any
        old_connection_id = None
        for conn_id, conn_info in self.connection_info.items():
            if conn_info.exam_id == exam_id and conn_info.invigilator_id == invigilator_id:
                old_connection_id = conn_id
                break
        
        if old_connection_id:
            # Find and remove old WebSocket connection
            for ws, conn_id in list(self.websocket_to_connection.items()):
                if conn_id == old_connection_id:
                    self.disconnect(ws)
                    break
        
        # Establish new connection
        await self.connect(websocket, exam_id, invigilator_id)
        
        # Resend missed messages if needed
        if last_message_id:
            await self.resend_missed_messages(websocket, last_message_id)
    
    async def resend_missed_messages(self, websocket: WebSocket, last_message_id: str):
        """Resend messages that were missed during disconnection"""
        # This would typically involve querying a message store
        # For now, we'll send a resync request
        await self.send_personal_message(websocket, {
            "type": "resync_request",
            "last_message_id": last_message_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _get_next_message_id(self) -> str:
        """Generate unique message ID for ordering"""
        self.message_id_counter += 1
        return f"msg_{self.message_id_counter}_{datetime.utcnow().timestamp()}"
    
    async def handle_ping(self, websocket: WebSocket):
        """Handle ping/pong for connection health"""
        await self.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_connection_count(self, exam_id: str) -> int:
        """Get number of active connections for an exam"""
        return len(self.active_connections.get(exam_id, set()))
    
    async def shutdown(self):
        """Cleanup all connections on shutdown"""
        for exam_id in list(self.active_connections.keys()):
            for websocket in self.active_connections[exam_id].copy():
                try:
                    await websocket.close()
                except:
                    pass
                self.disconnect(websocket)
        
        self.active_connections.clear()
        self.connection_info.clear()
        self.websocket_to_connection.clear()
        self.message_queue.clear()
        
        logger.info("WebSocket manager shutdown completed")


# Global instance
websocket_manager = WebSocketManager()
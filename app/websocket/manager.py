from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, exam_id: str):
        await websocket.accept()
        if exam_id not in self.active_connections:
            self.active_connections[exam_id] = set()
        self.active_connections[exam_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, exam_id: str):
        if exam_id in self.active_connections:
            self.active_connections[exam_id].discard(websocket)
            if not self.active_connections[exam_id]:
                del self.active_connections[exam_id]
    
    async def broadcast_risk_score(self, exam_id: str, session_id: str, risk_score: dict):
        if exam_id in self.active_connections:
            message = {
                "type": "risk_score_update",
                "exam_id": exam_id,
                "session_id": session_id,
                "score": risk_score["score"],
                "risk_level": risk_score["risk_level"],
                "alert_level": self._get_alert_level(risk_score["score"]),
                "contribution_breakdown": risk_score["contribution_breakdown"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            disconnected = set()
            for connection in self.active_connections[exam_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            for connection in disconnected:
                self.disconnect(connection, exam_id)
    
    def _get_alert_level(self, score: float) -> str:
        if score >= 75:
            return "red"
        elif score >= 50:
            return "yellow"
        else:
            return "green"


manager = ConnectionManager()

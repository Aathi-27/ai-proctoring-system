from fastapi import WebSocket
from typing import Dict, Set, Optional
import logging
import asyncio
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.exam_rooms: Dict[str, Set[str]] = {}
        self.candidate_sessions: Dict[str, WebSocket] = {}
        self.invigilator_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect_invigilator(self, websocket: WebSocket, exam_id: str, invigilator_id: str):
        await websocket.accept()
        connection_key = f"invigilator_{exam_id}_{invigilator_id}"
        
        async with self._lock:
            self.active_connections[connection_key] = websocket
            
            if exam_id not in self.invigilator_connections:
                self.invigilator_connections[exam_id] = set()
            self.invigilator_connections[exam_id].add(websocket)
            
            if exam_id not in self.exam_rooms:
                self.exam_rooms[exam_id] = set()
        
        logger.info(f"Invigilator {invigilator_id} connected to exam {exam_id}")
        
        await self.send_personal_message(
            websocket,
            {
                "type": "connect",
                "message": f"Connected to exam {exam_id}",
                "exam_id": exam_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def connect_candidate(self, websocket: WebSocket, session_id: str, exam_id: Optional[str] = None):
        await websocket.accept()
        
        async with self._lock:
            self.candidate_sessions[session_id] = websocket
            self.active_connections[f"candidate_{session_id}"] = websocket
            
            if exam_id and exam_id not in self.exam_rooms:
                self.exam_rooms[exam_id] = set()
            if exam_id:
                self.exam_rooms[exam_id].add(session_id)
        
        logger.info(f"Candidate {session_id} connected" + (f" to exam {exam_id}" if exam_id else ""))
        
        await self.send_personal_message(
            websocket,
            {
                "type": "connect",
                "message": "Connected successfully",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def disconnect(self, websocket: WebSocket, connection_key: str):
        async with self._lock:
            if connection_key in self.active_connections:
                del self.active_connections[connection_key]
            
            if connection_key.startswith("candidate_"):
                session_id = connection_key.replace("candidate_", "")
                if session_id in self.candidate_sessions:
                    del self.candidate_sessions[session_id]
                
                for exam_id, sessions in self.exam_rooms.items():
                    if session_id in sessions:
                        sessions.remove(session_id)
            
            elif connection_key.startswith("invigilator_"):
                for exam_id, connections in self.invigilator_connections.items():
                    if websocket in connections:
                        connections.remove(websocket)
                        break
        
        logger.info(f"Connection {connection_key} disconnected")

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def send_to_candidate(self, session_id: str, message: dict):
        if session_id in self.candidate_sessions:
            websocket = self.candidate_sessions[session_id]
            await self.send_personal_message(websocket, message)
        else:
            logger.warning(f"Candidate {session_id} not connected")

    async def broadcast_to_exam_invigilators(self, exam_id: str, message: dict):
        if exam_id not in self.invigilator_connections:
            logger.warning(f"No invigilators connected to exam {exam_id}")
            return
        
        disconnected = []
        for websocket in self.invigilator_connections[exam_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to invigilator: {e}")
                disconnected.append(websocket)
        
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    self.invigilator_connections[exam_id].discard(ws)

    async def broadcast_to_exam_candidates(self, exam_id: str, message: dict):
        if exam_id not in self.exam_rooms:
            logger.warning(f"No candidates in exam room {exam_id}")
            return
        
        disconnected = []
        for session_id in self.exam_rooms[exam_id]:
            if session_id in self.candidate_sessions:
                try:
                    await self.candidate_sessions[session_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to candidate {session_id}: {e}")
                    disconnected.append(session_id)
        
        if disconnected:
            async with self._lock:
                for session_id in disconnected:
                    if session_id in self.candidate_sessions:
                        del self.candidate_sessions[session_id]
                    self.exam_rooms[exam_id].discard(session_id)

    async def handle_reconnection(self, websocket: WebSocket, session_id: str, connection_type: str):
        logger.info(f"Handling reconnection for {connection_type} {session_id}")
        
        if connection_type == "candidate":
            await self.connect_candidate(websocket, session_id)
        
        await self.send_personal_message(
            websocket,
            {
                "type": "reconnect",
                "message": "Reconnected successfully",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def get_exam_candidates(self, exam_id: str) -> Set[str]:
        return self.exam_rooms.get(exam_id, set())

    def get_active_connection_count(self) -> int:
        return len(self.active_connections)

    def is_candidate_connected(self, session_id: str) -> bool:
        return session_id in self.candidate_sessions

    async def ping_connections(self):
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for key, websocket in self.active_connections.items():
            try:
                await websocket.send_json(ping_message)
            except Exception as e:
                logger.warning(f"Connection {key} failed ping: {e}")
                disconnected.append((key, websocket))
        
        for key, websocket in disconnected:
            await self.disconnect(websocket, key)


connection_manager = ConnectionManager()

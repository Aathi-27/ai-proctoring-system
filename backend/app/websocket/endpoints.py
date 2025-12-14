from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Path
from typing import Optional
import logging
import json
from datetime import datetime

from app.websocket.connection_manager import connection_manager
from app.models.websocket_models import (
    MessageType,
    AlertMessage,
    VideoFrameMessage,
    AudioChunkMessage,
    CandidateStatusMessage,
    StreamQualityMessage,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/exam/{exam_id}")
async def websocket_invigilator_endpoint(
    websocket: WebSocket,
    exam_id: str = Path(..., description="Exam ID"),
    invigilator_id: str = Query(..., description="Invigilator ID")
):
    connection_key = f"invigilator_{exam_id}_{invigilator_id}"
    
    try:
        await connection_manager.connect_invigilator(websocket, exam_id, invigilator_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == MessageType.PING:
                    await connection_manager.send_personal_message(
                        websocket,
                        {
                            "type": MessageType.PONG,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                
                elif message_type == "broadcast_to_candidates":
                    await connection_manager.broadcast_to_exam_candidates(
                        exam_id,
                        {
                            "type": "invigilator_message",
                            "data": message.get("data"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                
                else:
                    logger.debug(f"Received message from invigilator {invigilator_id}: {message_type}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from invigilator {invigilator_id}: {e}")
                await connection_manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
    
    except WebSocketDisconnect:
        logger.info(f"Invigilator {invigilator_id} disconnected from exam {exam_id}")
        await connection_manager.disconnect(websocket, connection_key)
    
    except Exception as e:
        logger.error(f"Error in invigilator websocket: {e}")
        await connection_manager.disconnect(websocket, connection_key)


@router.websocket("/ws/candidate/{session_id}")
async def websocket_candidate_endpoint(
    websocket: WebSocket,
    session_id: str = Path(..., description="Candidate session ID"),
    exam_id: Optional[str] = Query(None, description="Exam ID")
):
    connection_key = f"candidate_{session_id}"
    
    try:
        await connection_manager.connect_candidate(websocket, session_id, exam_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                message_data = message.get("data", {})
                
                if message_type == MessageType.PING:
                    await connection_manager.send_personal_message(
                        websocket,
                        {
                            "type": MessageType.PONG,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                
                elif message_type == MessageType.PERMISSION_GRANTED:
                    logger.info(f"Candidate {session_id} granted permissions")
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.CANDIDATE_STATUS,
                                "data": {
                                    "session_id": session_id,
                                    "status": "permissions_granted",
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.PERMISSION_DENIED:
                    logger.warning(f"Candidate {session_id} denied permissions")
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.ALERT,
                                "data": {
                                    "level": "warning",
                                    "message": f"Candidate {session_id} denied media permissions",
                                    "session_id": session_id,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.VIDEO_FRAME:
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.VIDEO_FRAME,
                                "data": {
                                    "session_id": session_id,
                                    "frame_data": message_data.get("frame_data"),
                                    "frame_number": message_data.get("frame_number"),
                                    "quality": message_data.get("quality", "medium"),
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.AUDIO_CHUNK:
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.AUDIO_CHUNK,
                                "data": {
                                    "session_id": session_id,
                                    "audio_data": message_data.get("audio_data"),
                                    "chunk_number": message_data.get("chunk_number"),
                                    "sample_rate": message_data.get("sample_rate", 48000),
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.CANDIDATE_STATUS:
                    logger.info(f"Candidate {session_id} status update: {message_data}")
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.CANDIDATE_STATUS,
                                "data": {
                                    "session_id": session_id,
                                    **message_data,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.STREAM_QUALITY:
                    logger.debug(f"Candidate {session_id} stream quality: {message_data}")
                    if exam_id:
                        await connection_manager.broadcast_to_exam_invigilators(
                            exam_id,
                            {
                                "type": MessageType.STREAM_QUALITY,
                                "data": {
                                    "session_id": session_id,
                                    **message_data,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                
                elif message_type == MessageType.CONNECTION_STATUS:
                    logger.info(f"Candidate {session_id} connection status: {message_data.get('status')}")
                
                else:
                    logger.debug(f"Received message from candidate {session_id}: {message_type}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from candidate {session_id}: {e}")
                await connection_manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
    
    except WebSocketDisconnect:
        logger.info(f"Candidate {session_id} disconnected")
        await connection_manager.disconnect(websocket, connection_key)
        
        if exam_id:
            await connection_manager.broadcast_to_exam_invigilators(
                exam_id,
                {
                    "type": MessageType.ALERT,
                    "data": {
                        "level": "info",
                        "message": f"Candidate {session_id} disconnected",
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
    
    except Exception as e:
        logger.error(f"Error in candidate websocket: {e}")
        await connection_manager.disconnect(websocket, connection_key)

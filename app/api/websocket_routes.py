import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse

from app.services.websocket_manager import websocket_manager
from app.services.alert_service import alert_service
from app.models.alerts import AlertAcknowledgmentRequest, AlertQueryRequest


logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/exam/{exam_id}")
async def websocket_exam_endpoint(websocket: WebSocket, exam_id: str):
    """WebSocket endpoint for real-time alerts for an exam"""
    invigilator_id = None
    
    try:
        # Extract invigilator ID from query parameters or headers
        invigilator_id = websocket.query_params.get("invigilator_id")
        if not invigilator_id:
            invigilator_id = "unknown"
        
        # Extract last message ID for reconnection
        last_message_id = websocket.query_params.get("last_message_id")
        
        # Establish connection
        if last_message_id:
            # Handle reconnection
            await websocket_manager.handle_reconnection(
                websocket, exam_id, invigilator_id, last_message_id
            )
        else:
            # New connection
            connection_id = await websocket_manager.connect(
                websocket, exam_id, invigilator_id
            )
            
            logger.info(f"WebSocket connection established: {connection_id}")
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "ping":
                    await websocket_manager.handle_ping(websocket)
                    
                elif message_type == "acknowledge_alert":
                    # Acknowledge alert
                    alert_id = message.get("alert_id")
                    if alert_id:
                        success = await alert_service.acknowledge_alert(alert_id, invigilator_id)
                        await websocket_manager.send_acknowledgment(websocket, alert_id, success)
                    else:
                        await websocket_manager.send_acknowledgment(websocket, "", False)
                
                elif message_type == "get_alerts":
                    # Get alert history
                    query_request = AlertQueryRequest(
                        exam_id=exam_id,
                        session_id=message.get("session_id"),
                        severity=message.get("severity"),
                        event_type=message.get("event_type"),
                        limit=message.get("limit", 100),
                        offset=message.get("offset", 0)
                    )
                    
                    alerts = await alert_service.query_alerts(query_request)
                    
                    await websocket_manager.send_personal_message(websocket, {
                        "type": "alert_history",
                        "alerts": [alert.dict() for alert in alerts],
                        "count": len(alerts)
                    })
                
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from WebSocket")
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {exam_id}/{invigilator_id}")
                break
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": f"Internal server error: {str(e)}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {exam_id}/{invigilator_id}")
        
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if not websocket.client_state.check_disconnected():
            try:
                await websocket.close(code=1011, reason="Internal server error")
            except:
                pass
    
    finally:
        # Cleanup connection
        websocket_manager.disconnect(websocket)
        logger.info(f"WebSocket connection cleaned up: {exam_id}/{invigilator_id}")


@router.post("/exams/{exam_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(exam_id: str, alert_id: str, request: AlertAcknowledgmentRequest):
    """REST endpoint for acknowledging alerts"""
    try:
        # Validate that the alert belongs to the exam
        alert = await alert_service.get_alert_by_id(alert_id)
        if not alert or alert.exam_id != exam_id:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Acknowledge the alert
        success = await alert_service.acknowledge_alert(alert_id, request.invigilator_id)
        
        if success:
            return {"message": "Alert acknowledged successfully", "alert_id": alert_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to acknowledge alert")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exams/{exam_id}/alerts")
async def get_exam_alerts(exam_id: str, session_id: str = None, severity: str = None, 
                        event_type: str = None, limit: int = 100, offset: int = 0):
    """REST endpoint for retrieving alert history"""
    try:
        from app.models.alerts import AlertSeverity, AlertType
        
        # Convert string enums if provided
        severity_enum = AlertSeverity(severity) if severity else None
        event_type_enum = AlertType(event_type) if event_type else None
        
        query_request = AlertQueryRequest(
            exam_id=exam_id,
            session_id=session_id,
            severity=severity_enum,
            event_type=event_type_enum,
            limit=limit,
            offset=offset
        )
        
        alerts = await alert_service.query_alerts(query_request)
        
        return {
            "exam_id": exam_id,
            "alerts": [alert.dict() for alert in alerts],
            "count": len(alerts),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(alerts) == limit
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get exam alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exams/{exam_id}/alerts/{alert_id}")
async def get_alert_by_id(exam_id: str, alert_id: str):
    """REST endpoint for getting a specific alert"""
    try:
        alert = await alert_service.get_alert_by_id(alert_id)
        if not alert or alert.exam_id != exam_id:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return alert.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alert by ID: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exams/{exam_id}/alerts/critical-count")
async def get_critical_alerts_count(exam_id: str):
    """REST endpoint for getting count of unacknowledged critical alerts"""
    try:
        count = await alert_service.get_critical_alerts_count(exam_id)
        return {"exam_id": exam_id, "critical_alerts_count": count}
        
    except Exception as e:
        logger.error(f"Failed to get critical alerts count: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exams/{exam_id}/risk-score")
async def get_risk_score(exam_id: str):
    """REST endpoint for getting current risk score"""
    try:
        risk_score = await alert_service.get_risk_score(exam_id)
        return {"exam_id": exam_id, "risk_score": risk_score}
        
    except Exception as e:
        logger.error(f"Failed to get risk score: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/exams/{exam_id}/monitoring/start")
async def start_exam_monitoring(exam_id: str, session_id: str):
    """REST endpoint for starting exam monitoring"""
    try:
        success = await alert_service.start_exam_monitoring(exam_id, session_id)
        if success:
            return {"message": "Exam monitoring started", "exam_id": exam_id, "session_id": session_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to start monitoring")
            
    except Exception as e:
        logger.error(f"Failed to start exam monitoring: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/exams/{exam_id}/monitoring/end")
async def end_exam_monitoring(exam_id: str, session_id: str):
    """REST endpoint for ending exam monitoring"""
    try:
        success = await alert_service.end_exam_monitoring(exam_id, session_id)
        if success:
            return {"message": "Exam monitoring ended", "exam_id": exam_id, "session_id": session_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to end monitoring")
            
    except Exception as e:
        logger.error(f"Failed to end exam monitoring: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exams/{exam_id}/invigilators")
async def get_connected_invigilators(exam_id: str):
    """REST endpoint for getting connected invigilators"""
    try:
        invigilators = websocket_manager.get_connected_invigilators(exam_id)
        connection_count = websocket_manager.get_connection_count(exam_id)
        
        return {
            "exam_id": exam_id,
            "connected_invigilators": [invigilator.dict() for invigilator in invigilators],
            "connection_count": connection_count
        }
        
    except Exception as e:
        logger.error(f"Failed to get connected invigilators: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ws/health")
async def websocket_health():
    """Health check for WebSocket service"""
    try:
        return {
            "status": "healthy",
            "websocket_manager": "active",
            "alert_service": "active",
            "timestamp": "2025-01-15T14:23:45Z"
        }
        
    except Exception as e:
        logger.error(f"WebSocket health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")
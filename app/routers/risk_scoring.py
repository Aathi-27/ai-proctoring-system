from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.models.events import (
    DetectionEvent,
    RiskScoreResponse,
    RiskTimelineResponse,
    ScoreBreakdownResponse,
    EventContribution
)
from app.services.risk_scoring import risk_scoring_engine
from app.websocket.manager import manager
from datetime import datetime


router = APIRouter(prefix="/exams", tags=["risk-scoring"])


@router.post("/{exam_id}/events")
async def receive_detection_event(exam_id: str, event: DetectionEvent):
    if event.exam_id != exam_id:
        raise HTTPException(status_code=400, detail="Exam ID mismatch")
    
    await risk_scoring_engine.save_detection_event(event)
    
    risk_score = await risk_scoring_engine.compute_risk_score(
        exam_id=event.exam_id,
        session_id=event.session_id
    )
    
    risk_score_dict = {
        "score": risk_score.score,
        "risk_level": risk_score.risk_level,
        "contribution_breakdown": [
            contrib.model_dump() for contrib in risk_score.contribution_breakdown
        ]
    }
    
    await manager.broadcast_risk_score(
        exam_id=exam_id,
        session_id=event.session_id,
        risk_score=risk_score_dict
    )
    
    return {
        "message": "Event received and processed",
        "risk_score": risk_score.score,
        "risk_level": risk_score.risk_level
    }


@router.post("/{exam_id}/compute-risk")
async def compute_risk_score(exam_id: str, session_id: str):
    try:
        risk_score = await risk_scoring_engine.compute_risk_score(
            exam_id=exam_id,
            session_id=session_id
        )
        
        risk_score_dict = {
            "score": risk_score.score,
            "risk_level": risk_score.risk_level,
            "contribution_breakdown": [
                contrib.model_dump() for contrib in risk_score.contribution_breakdown
            ]
        }
        
        await manager.broadcast_risk_score(
            exam_id=exam_id,
            session_id=session_id,
            risk_score=risk_score_dict
        )
        
        return {
            "exam_id": exam_id,
            "session_id": session_id,
            "score": risk_score.score,
            "risk_level": risk_score.risk_level,
            "timestamp": risk_score.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exam_id}/sessions/{session_id}/risk-score", response_model=RiskScoreResponse)
async def get_current_risk_score(exam_id: str, session_id: str):
    try:
        risk_score = await risk_scoring_engine.get_current_risk_score(
            exam_id=exam_id,
            session_id=session_id
        )
        
        return RiskScoreResponse(
            exam_id=exam_id,
            session_id=session_id,
            current_score=risk_score.score,
            risk_level=risk_score.risk_level,
            last_updated=risk_score.timestamp,
            contribution_breakdown=risk_score.contribution_breakdown
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exam_id}/sessions/{session_id}/risk-timeline", response_model=RiskTimelineResponse)
async def get_risk_timeline(exam_id: str, session_id: str, limit: int = 100):
    try:
        timeline = await risk_scoring_engine.get_risk_timeline(
            exam_id=exam_id,
            session_id=session_id,
            limit=limit
        )
        
        return RiskTimelineResponse(
            exam_id=exam_id,
            session_id=session_id,
            timeline=timeline
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exam_id}/sessions/{session_id}/score-breakdown", response_model=ScoreBreakdownResponse)
async def get_score_breakdown(exam_id: str, session_id: str):
    try:
        risk_score = await risk_scoring_engine.compute_risk_score(
            exam_id=exam_id,
            session_id=session_id
        )
        
        return ScoreBreakdownResponse(
            exam_id=exam_id,
            session_id=session_id,
            current_score=risk_score.score,
            risk_level=risk_score.risk_level,
            total_events=len(risk_score.contribution_breakdown),
            contribution_breakdown=risk_score.contribution_breakdown,
            active_events_in_window=len(risk_score.contribution_breakdown)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/{exam_id}/ws")
async def websocket_endpoint(websocket: WebSocket, exam_id: str):
    await manager.connect(websocket, exam_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, exam_id)

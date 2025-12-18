from datetime import datetime, timedelta
from typing import List, Dict
import math
from app.models.events import DetectionEvent, RiskScore, EventContribution
from app.config import settings
from app.database.mongodb import get_database


class RiskScoringEngine:
    def __init__(self):
        self.event_weights = settings.event_weights
        self.window_minutes = settings.risk_score_window_minutes
        self.decay_factor = settings.time_decay_factor
    
    def calculate_time_decay(self, event_timestamp: datetime, current_time: datetime) -> float:
        time_diff_minutes = (current_time - event_timestamp).total_seconds() / 60.0
        
        if time_diff_minutes < 0:
            return 1.0
        
        if time_diff_minutes >= self.window_minutes:
            return 0.0
        
        decay = math.exp(-self.decay_factor * (time_diff_minutes / self.window_minutes))
        return decay
    
    def get_event_weight(self, event_type: str) -> int:
        return self.event_weights.get(event_type, 0)
    
    def calculate_contribution(
        self, 
        event: DetectionEvent, 
        current_time: datetime
    ) -> EventContribution:
        weight = self.get_event_weight(event.event_type.value)
        time_decay = self.calculate_time_decay(event.timestamp, current_time)
        contribution = event.confidence * weight * time_decay
        
        return EventContribution(
            event=event.event_type.value,
            confidence=event.confidence,
            weight=weight,
            contribution=round(contribution, 2),
            timestamp=event.timestamp
        )
    
    async def compute_risk_score(
        self, 
        exam_id: str, 
        session_id: str,
        current_time: datetime = None
    ) -> RiskScore:
        if current_time is None:
            current_time = datetime.utcnow()
        
        db = get_database()
        
        window_start = current_time - timedelta(minutes=self.window_minutes)
        
        events_cursor = db.detection_events.find({
            "exam_id": exam_id,
            "session_id": session_id,
            "timestamp": {"$gte": window_start, "$lte": current_time}
        }).sort("timestamp", -1)
        
        events = await events_cursor.to_list(length=None)
        
        contribution_breakdown = []
        total_score = 0.0
        
        for event_doc in events:
            event = DetectionEvent(**event_doc)
            contribution = self.calculate_contribution(event, current_time)
            
            if contribution.contribution > 0:
                contribution_breakdown.append(contribution)
                total_score += contribution.contribution
        
        final_score = min(100.0, total_score)
        risk_level = RiskScore.get_risk_level(final_score)
        
        risk_score = RiskScore(
            exam_id=exam_id,
            session_id=session_id,
            score=round(final_score, 2),
            risk_level=risk_level,
            contribution_breakdown=contribution_breakdown,
            timestamp=current_time
        )
        
        await self.save_risk_score(risk_score)
        
        return risk_score
    
    async def save_risk_score(self, risk_score: RiskScore):
        db = get_database()
        
        score_dict = risk_score.model_dump()
        score_dict["contribution_breakdown"] = [
            contrib.model_dump() for contrib in risk_score.contribution_breakdown
        ]
        
        await db.risk_score_history.insert_one(score_dict)
    
    async def save_detection_event(self, event: DetectionEvent):
        db = get_database()
        event_dict = event.model_dump()
        await db.detection_events.insert_one(event_dict)
    
    async def get_current_risk_score(self, exam_id: str, session_id: str) -> RiskScore:
        db = get_database()
        
        latest_score = await db.risk_score_history.find_one(
            {"exam_id": exam_id, "session_id": session_id},
            sort=[("timestamp", -1)]
        )
        
        if not latest_score:
            return await self.compute_risk_score(exam_id, session_id)
        
        latest_score.pop("_id", None)
        latest_score["contribution_breakdown"] = [
            EventContribution(**contrib) for contrib in latest_score.get("contribution_breakdown", [])
        ]
        
        return RiskScore(**latest_score)
    
    async def get_risk_timeline(
        self, 
        exam_id: str, 
        session_id: str, 
        limit: int = 100
    ) -> List[RiskScore]:
        db = get_database()
        
        scores_cursor = db.risk_score_history.find(
            {"exam_id": exam_id, "session_id": session_id}
        ).sort("timestamp", -1).limit(limit)
        
        scores = await scores_cursor.to_list(length=limit)
        
        risk_scores = []
        for score_doc in scores:
            score_doc.pop("_id", None)
            score_doc["contribution_breakdown"] = [
                EventContribution(**contrib) for contrib in score_doc.get("contribution_breakdown", [])
            ]
            risk_scores.append(RiskScore(**score_doc))
        
        return risk_scores
    
    def get_alert_level(self, score: float) -> str:
        if score >= 75:
            return "red"
        elif score >= 50:
            return "yellow"
        else:
            return "green"


risk_scoring_engine = RiskScoringEngine()

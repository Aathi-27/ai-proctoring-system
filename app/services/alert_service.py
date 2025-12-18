import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.models.alerts import (
    AlertEvent, AlertSeverity, AlertType, EvidenceSnapshot, 
    AlertAcknowledgmentRequest, AlertQueryRequest
)
from app.services.websocket_manager import websocket_manager
from app.services.evidence_service import evidence_service
from app.database.mongodb import MongoDBClient


logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing alerts, event streaming, and evidence capture"""
    
    def __init__(self):
        from app.database.mongodb import mongodb_client
        self.mongodb = mongodb_client
        self.alert_rules = self._initialize_alert_rules()
        self.risk_score_cache: Dict[str, int] = {}
        
    def _initialize_alert_rules(self) -> Dict[AlertType, Dict[str, Any]]:
        """Initialize alert rules and configurations"""
        return {
            AlertType.MOBILE_DETECTED: {
                "severity": AlertSeverity.CRITICAL,
                "risk_score_delta": 25,
                "require_snapshot": True,
                "confidence_threshold": 0.8,
                "description": "Mobile phone detected in camera frame"
            },
            AlertType.MULTIPLE_FACES: {
                "severity": AlertSeverity.CRITICAL,
                "risk_score_delta": 20,
                "require_snapshot": True,
                "confidence_threshold": 0.7,
                "description": "Multiple faces detected in camera frame"
            },
            AlertType.BACKGROUND_SPEECH: {
                "severity": AlertSeverity.CRITICAL,
                "risk_score_delta": 15,
                "require_snapshot": False,
                "confidence_threshold": 0.8,
                "description": "Background speech detected"
            },
            AlertType.TAB_SWITCH: {
                "severity": AlertSeverity.WARNING,
                "risk_score_delta": 10,
                "require_snapshot": False,
                "confidence_threshold": 0.9,
                "description": "Tab switch detected during exam"
            },
            AlertType.INACTIVITY: {
                "severity": AlertSeverity.WARNING,
                "risk_score_delta": 8,
                "require_snapshot": False,
                "confidence_threshold": 0.8,
                "description": "User inactivity detected"
            },
            AlertType.FACE_NOT_DETECTED: {
                "severity": AlertSeverity.WARNING,
                "risk_score_delta": 12,
                "require_snapshot": True,
                "confidence_threshold": 0.6,
                "description": "Face not detected in camera frame"
            },
            AlertType.LIVENESS_CONFIRMED: {
                "severity": AlertSeverity.INFO,
                "risk_score_delta": -5,
                "require_snapshot": False,
                "confidence_threshold": 0.8,
                "description": "Liveness verification successful"
            },
            AlertType.NORMAL_ACTIVITY: {
                "severity": AlertSeverity.INFO,
                "risk_score_delta": -2,
                "require_snapshot": False,
                "confidence_threshold": 0.8,
                "description": "Normal exam activity detected"
            },
            AlertType.EXAM_STARTED: {
                "severity": AlertSeverity.INFO,
                "risk_score_delta": 0,
                "require_snapshot": False,
                "confidence_threshold": 1.0,
                "description": "Exam session started"
            },
            AlertType.EXAM_ENDED: {
                "severity": AlertSeverity.INFO,
                "risk_score_delta": 0,
                "require_snapshot": False,
                "confidence_threshold": 1.0,
                "description": "Exam session ended"
            }
        }
    
    async def generate_alert(
        self,
        exam_id: str,
        session_id: str,
        event_type: AlertType,
        confidence: float,
        event_data: Optional[Dict[str, Any]] = None,
        frame_data: Optional[str] = None,
        frame_number: Optional[int] = None
    ) -> Optional[AlertEvent]:
        """Generate and broadcast alert based on event type"""
        try:
            # Get alert rules for this event type
            if event_type not in self.alert_rules:
                logger.error(f"No alert rules defined for event type: {event_type}")
                return None
            
            rules = self.alert_rules[event_type]
            
            # Check confidence threshold
            if confidence < rules["confidence_threshold"]:
                logger.debug(f"Event {event_type} confidence {confidence} below threshold {rules['confidence_threshold']}")
                return None
            
            # Calculate current risk score
            current_risk_score = await self._calculate_risk_score(exam_id)
            
            # Create alert event
            alert = AlertEvent(
                exam_id=exam_id,
                session_id=session_id,
                event_type=event_type,
                severity=rules["severity"],
                confidence=confidence,
                risk_score_delta=rules["risk_score_delta"],
                current_risk_score=current_risk_score + rules["risk_score_delta"],
                message=rules["description"]
            )
            
            # Capture evidence snapshot if required
            if rules["require_snapshot"] and frame_data and frame_number:
                snapshot = await evidence_service.capture_snapshot(
                    frame_data=frame_data,
                    exam_id=exam_id,
                    session_id=session_id,
                    alert_id=alert.alert_id,
                    event_type=event_type,
                    frame_number=frame_number,
                    risk_score=alert.current_risk_score
                )
                
                if snapshot:
                    alert.evidence_snapshot_id = snapshot.snapshot_id
                    logger.info(f"Evidence snapshot captured for alert {alert.alert_id}")
            
            # Store alert in database
            stored_alert = await self._store_alert(alert)
            if not stored_alert:
                logger.error(f"Failed to store alert {alert.alert_id}")
                return None
            
            # Broadcast to connected invigilators
            await websocket_manager.broadcast_alert(exam_id, alert)
            
            # Update risk score cache
            await self._update_risk_score_cache(exam_id, alert.current_risk_score)
            
            logger.info(f"Alert generated and broadcast: {event_type} for exam {exam_id}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Failed to generate alert: {e}")
            return None
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        invigilator_id: str
    ) -> bool:
        """Acknowledge an alert"""
        try:
            # Update alert in database
            result = await self.mongodb.alerts.update_one(
                {"alert_id": alert_id},
                {
                    "$set": {
                        "acknowledged": True,
                        "acknowledged_by": invigilator_id,
                        "acknowledged_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Alert {alert_id} acknowledged by {invigilator_id}")
                return True
            else:
                logger.warning(f"Alert {alert_id} not found or already acknowledged")
                return False
                
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def query_alerts(self, request: AlertQueryRequest) -> List[AlertEvent]:
        """Query alert history"""
        try:
            # Build query filters
            query_filter = {"exam_id": request.exam_id}
            
            if request.session_id:
                query_filter["session_id"] = request.session_id
            
            if request.severity:
                query_filter["severity"] = request.severity
            
            if request.event_type:
                query_filter["event_type"] = request.event_type
            
            # Query database
            cursor = self.mongodb.alerts.find(query_filter).sort("timestamp", -1)
            
            if request.offset:
                cursor = cursor.skip(request.offset)
            
            if request.limit:
                cursor = cursor.limit(request.limit)
            
            # Convert to alert events
            alerts = []
            async for doc in cursor:
                alert = self._dict_to_alert_event(doc)
                if alert:
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to query alerts: {e}")
            return []
    
    async def get_alert_by_id(self, alert_id: str) -> Optional[AlertEvent]:
        """Get alert by ID"""
        try:
            doc = await self.mongodb.alerts.find_one({"alert_id": alert_id})
            return self._dict_to_alert_event(doc) if doc else None
            
        except Exception as e:
            logger.error(f"Failed to get alert {alert_id}: {e}")
            return None
    
    async def get_alerts_by_session(self, session_id: str) -> List[AlertEvent]:
        """Get all alerts for a specific session"""
        try:
            cursor = self.mongodb.alerts.find({"session_id": session_id}).sort("timestamp", -1)
            
            alerts = []
            async for doc in cursor:
                alert = self._dict_to_alert_event(doc)
                if alert:
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts for session {session_id}: {e}")
            return []
    
    async def get_critical_alerts_count(self, exam_id: str) -> int:
        """Get count of unacknowledged critical alerts for an exam"""
        try:
            count = await self.mongodb.alerts.count_documents({
                "exam_id": exam_id,
                "severity": AlertSeverity.CRITICAL,
                "acknowledged": False
            })
            return count
            
        except Exception as e:
            logger.error(f"Failed to get critical alerts count for exam {exam_id}: {e}")
            return 0
    
    async def get_risk_score(self, exam_id: str) -> int:
        """Get current risk score for an exam"""
        return await self._calculate_risk_score(exam_id)
    
    async def start_exam_monitoring(self, exam_id: str, session_id: str) -> bool:
        """Initialize exam monitoring session"""
        try:
            # Initialize risk score cache
            self.risk_score_cache[exam_id] = 0
            
            # Generate exam started alert
            await self.generate_alert(
                exam_id=exam_id,
                session_id=session_id,
                event_type=AlertType.EXAM_STARTED,
                confidence=1.0
            )
            
            logger.info(f"Exam monitoring started for {exam_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start exam monitoring: {e}")
            return False
    
    async def end_exam_monitoring(self, exam_id: str, session_id: str) -> bool:
        """End exam monitoring session"""
        try:
            # Generate exam ended alert
            await self.generate_alert(
                exam_id=exam_id,
                session_id=session_id,
                event_type=AlertType.EXAM_ENDED,
                confidence=1.0
            )
            
            # Clean up cache
            if exam_id in self.risk_score_cache:
                del self.risk_score_cache[exam_id]
            
            logger.info(f"Exam monitoring ended for {exam_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end exam monitoring: {e}")
            return False
    
    async def _calculate_risk_score(self, exam_id: str) -> int:
        """Calculate current risk score for an exam"""
        try:
            # Get from cache if available
            if exam_id in self.risk_score_cache:
                return self.risk_score_cache[exam_id]
            
            # Calculate from recent alerts (last 5 minutes)
            five_minutes_ago = datetime.utcnow().timestamp() - (5 * 60)
            
            pipeline = [
                {"$match": {
                    "exam_id": exam_id,
                    "timestamp": {"$gte": datetime.fromtimestamp(five_minutes_ago)}
                }},
                {"$group": {
                    "_id": None,
                    "total_risk_delta": {"$sum": "$risk_score_delta"}
                }}
            ]
            
            result = await self.mongodb.alerts.aggregate(pipeline).to_list(length=1)
            
            if result:
                risk_score = max(0, min(100, result[0]["total_risk_delta"]))
            else:
                risk_score = 0
            
            # Update cache
            self.risk_score_cache[exam_id] = risk_score
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score for {exam_id}: {e}")
            return 0
    
    async def _update_risk_score_cache(self, exam_id: str, risk_score: int):
        """Update risk score cache"""
        self.risk_score_cache[exam_id] = risk_score
    
    async def _store_alert(self, alert: AlertEvent) -> bool:
        """Store alert in database"""
        try:
            alert_dict = alert.dict()
            await self.mongodb.alerts.insert_one(alert_dict)
            return True
            
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
            return False
    
    def _dict_to_alert_event(self, doc: dict) -> Optional[AlertEvent]:
        """Convert database document to AlertEvent"""
        try:
            if not doc:
                return None
            
            # Handle ObjectId serialization
            doc["alert_id"] = doc.get("alert_id", str(doc.get("_id", "")))
            if "_id" in doc:
                del doc["_id"]
            
            return AlertEvent(**doc)
            
        except Exception as e:
            logger.error(f"Failed to convert dict to AlertEvent: {e}")
            return None
    
    async def cleanup_expired_data(self):
        """Cleanup expired snapshots and old alerts"""
        try:
            # Cleanup expired snapshots
            await evidence_service.delete_expired_snapshots()
            
            # TODO: Cleanup old alert records based on retention policy
            
            logger.info("Cleanup of expired data completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")


# Global instance
alert_service = AlertService()
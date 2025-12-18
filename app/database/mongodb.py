import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client for the application"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.connected = False
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Get MongoDB configuration from environment
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "ai_proctoring")
            
            # Create async MongoDB client
            self.client = AsyncIOMotorClient(mongodb_uri)
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[database_name]
            
            # Initialize collections
            self.alerts = self.database.alerts
            self.evidence_snapshots = self.database.evidence_snapshots
            self.exam_sessions = self.database.exam_sessions
            self.invigilator_connections = self.database.invigilator_connections
            
            # Create indexes
            await self._create_indexes()
            
            self.connected = True
            logger.info(f"Connected to MongoDB: {mongodb_uri}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.connected = False
            raise
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB connection closed")
    
    async def _create_indexes(self):
        """Create necessary database indexes for performance"""
        try:
            # Alerts collection indexes
            await self.alerts.create_index("exam_id")
            await self.alerts.create_index("session_id")
            await self.alerts.create_index("timestamp")
            await self.alerts.create_index("severity")
            await self.alerts.create_index("event_type")
            await self.alerts.create_index("acknowledged")
            await self.alerts.create_index([("exam_id", 1), ("timestamp", -1)])
            await self.alerts.create_index([("exam_id", 1), ("severity", 1), ("acknowledged", 1)])
            
            # Evidence snapshots indexes
            await self.evidence_snapshots.create_index("exam_id")
            await self.evidence_snapshots.create_index("session_id")
            await self.evidence_snapshots.create_index("alert_id")
            await self.evidence_snapshots.create_index("retention_expires_at")
            await self.evidence_snapshots.create_index([("exam_id", 1), ("timestamp", -1)])
            
            # Exam sessions indexes
            await self.exam_sessions.create_index("exam_id", unique=True)
            await self.exam_sessions.create_index("session_id")
            await self.exam_sessions.create_index("start_time")
            await self.exam_sessions.create_index("status")
            
            # Invigilator connections indexes
            await self.invigilator_connections.create_index("connection_id", unique=True)
            await self.invigilator_connections.create_index("exam_id")
            await self.invigilator_connections.create_index("invigilator_id")
            await self.invigilator_connections.create_index("connected_at")
            await self.invigilator_connections.create_index([("exam_id", 1), ("status", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def insert_alert(self, alert_data: dict) -> str:
        """Insert alert into database"""
        try:
            result = await self.alerts.insert_one(alert_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.warning(f"Alert already exists: {alert_data.get('alert_id')}")
            return alert_data.get('alert_id')
        except Exception as e:
            logger.error(f"Failed to insert alert: {e}")
            raise
    
    async def update_alert(self, alert_id: str, update_data: dict) -> bool:
        """Update alert in database"""
        try:
            result = await self.alerts.update_one(
                {"alert_id": alert_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update alert {alert_id}: {e}")
            return False
    
    async def find_alert(self, alert_id: str) -> Optional[dict]:
        """Find alert by ID"""
        try:
            return await self.alerts.find_one({"alert_id": alert_id})
        except Exception as e:
            logger.error(f"Failed to find alert {alert_id}: {e}")
            return None
    
    async def find_alerts(self, query: dict, limit: int = 100, offset: int = 0) -> list:
        """Find alerts with query"""
        try:
            cursor = self.alerts.find(query).sort("timestamp", -1)
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Failed to find alerts: {e}")
            return []
    
    async def count_alerts(self, query: dict) -> int:
        """Count alerts matching query"""
        try:
            return await self.alerts.count_documents(query)
        except Exception as e:
            logger.error(f"Failed to count alerts: {e}")
            return 0
    
    async def insert_evidence_snapshot(self, snapshot_data: dict) -> str:
        """Insert evidence snapshot metadata"""
        try:
            result = await self.evidence_snapshots.insert_one(snapshot_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert evidence snapshot: {e}")
            raise
    
    async def find_expired_snapshots(self) -> list:
        """Find snapshots that have expired"""
        try:
            from datetime import datetime
            current_time = datetime.utcnow()
            return await self.evidence_snapshots.find({
                "retention_expires_at": {"$lt": current_time}
            }).to_list(length=None)
        except Exception as e:
            logger.error(f"Failed to find expired snapshots: {e}")
            return []
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot metadata"""
        try:
            result = await self.evidence_snapshots.delete_one({"snapshot_id": snapshot_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False
    
    async def create_exam_session(self, session_data: dict) -> bool:
        """Create new exam session"""
        try:
            await self.exam_sessions.insert_one(session_data)
            return True
        except DuplicateKeyError:
            logger.warning(f"Exam session already exists: {session_data.get('exam_id')}")
            return False
        except Exception as e:
            logger.error(f"Failed to create exam session: {e}")
            return False
    
    async def update_exam_session(self, exam_id: str, update_data: dict) -> bool:
        """Update exam session"""
        try:
            result = await self.exam_sessions.update_one(
                {"exam_id": exam_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update exam session {exam_id}: {e}")
            return False
    
    async def get_exam_session(self, exam_id: str) -> Optional[dict]:
        """Get exam session"""
        try:
            return await self.exam_sessions.find_one({"exam_id": exam_id})
        except Exception as e:
            logger.error(f"Failed to get exam session {exam_id}: {e}")
            return None
    
    async def store_invigilator_connection(self, connection_data: dict) -> bool:
        """Store invigilator connection info"""
        try:
            await self.invigilator_connections.insert_one(connection_data)
            return True
        except DuplicateKeyError:
            # Update existing connection
            result = await self.invigilator_connections.update_one(
                {"connection_id": connection_data["connection_id"]},
                {"$set": connection_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to store invigilator connection: {e}")
            return False
    
    async def remove_invigilator_connection(self, connection_id: str) -> bool:
        """Remove invigilator connection"""
        try:
            result = await self.invigilator_connections.delete_one({"connection_id": connection_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to remove invigilator connection {connection_id}: {e}")
            return False
    
    async def get_connection_count(self, exam_id: str) -> int:
        """Get active connection count for exam"""
        try:
            return await self.invigilator_connections.count_documents({
                "exam_id": exam_id,
                "status": "connected"
            })
        except Exception as e:
            logger.error(f"Failed to get connection count for {exam_id}: {e}")
            return 0
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.client is not None


# Global instance
mongodb_client = MongoDBClient()
"""
MongoDB event storage for detection events.

Async MongoDB operations for storing and retrieving detection events.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    logger.warning("Motor not available. Install with: pip install motor")

from ..config.settings import mongodb_config
from ..models import DetectionEvent


class EventStorage:
    """MongoDB-based event storage for detection events."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
        self.is_connected = False
    
    async def connect(self):
        """Establish connection to MongoDB."""
        if not MONGO_AVAILABLE:
            logger.warning("Motor not available. Running in mock mode.")
            return
        
        try:
            # Build connection string
            if mongodb_config.username and mongodb_config.password:
                connection_string = (
                    f"mongodb://{mongodb_config.username}:{mongodb_config.password}"
                    f"@{mongodb_config.host}:{mongodb_config.port}/{mongodb_config.database}"
                )
            else:
                connection_string = (
                    f"mongodb://{mongodb_config.host}:{mongodb_config.port}"
                )
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(connection_string)
            self.database = self.client[mongodb_config.database]
            self.collection = self.database[mongodb_config.collection]
            
            # Create indexes
            await self._create_indexes()
            
            self.is_connected = True
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.warning("Running without MongoDB connection")
            self.is_connected = False
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better query performance."""
        try:
            # Index for efficient time-based queries
            await self.collection.create_index([("timestamp", -1)])
            
            # Index for exam queries
            await self.collection.create_index([("metadata.exam_id", 1)])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
    
    async def store_event(self, event: DetectionEvent) -> str:
        """Store a detection event in MongoDB."""
        if not self.is_connected:
            return "mock_event_id"
        
        try:
            # Convert event to dictionary
            event_dict = {
                "event_type": event.event_type,
                "object_type": event.object_type,
                "confidence": event.confidence,
                "bbox": event.bbox,
                "timestamp": datetime.fromtimestamp(event.timestamp),
                "frame_id": event.frame_id,
                "risk_score": event.risk_score,
                "metadata": event.metadata or {}
            }
            
            # Insert document
            result = await self.collection.insert_one(event_dict)
            
            logger.debug(f"Stored detection event: {event.event_type}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to store detection event: {e}")
            raise
    
    async def store_events_batch(self, events: List[DetectionEvent]) -> List[str]:
        """Store multiple detection events in MongoDB."""
        if not self.is_connected:
            return ["mock_event_id"] * len(events)
        
        if not events:
            return []
        
        try:
            # Convert events to dictionaries
            event_dicts = []
            for event in events:
                event_dict = {
                    "event_type": event.event_type,
                    "object_type": event.object_type,
                    "confidence": event.confidence,
                    "bbox": event.bbox,
                    "timestamp": datetime.fromtimestamp(event.timestamp),
                    "frame_id": event.frame_id,
                    "risk_score": event.risk_score,
                    "metadata": event.metadata or {}
                }
                event_dicts.append(event_dict)
            
            # Insert documents
            result = await self.collection.insert_many(event_dicts)
            
            ids = [str(id) for id in result.inserted_ids]
            logger.debug(f"Stored {len(events)} detection events")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to store detection events batch: {e}")
            raise
    
    async def get_events(self, 
                        exam_id: Optional[str] = None,
                        event_type: Optional[str] = None,
                        limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve detection events from MongoDB."""
        if not self.is_connected:
            return []
        
        try:
            # Build query filter
            query_filter = {}
            
            if exam_id:
                query_filter["metadata.exam_id"] = exam_id
            
            if event_type:
                query_filter["event_type"] = event_type
            
            # Execute query
            cursor = self.collection.find(query_filter).sort("timestamp", -1).limit(limit)
            events = await cursor.to_list(length=limit)
            
            # Convert datetime objects to timestamps for JSON serialization
            for event in events:
                if "timestamp" in event and isinstance(event["timestamp"], datetime):
                    event["timestamp"] = event["timestamp"].timestamp()
            
            logger.debug(f"Retrieved {len(events)} detection events")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve detection events: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health."""
        if not self.is_connected:
            return {
                "status": "unhealthy",
                "error": "MongoDB not connected",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Simple ping command
            await self.client.admin.command('ping')
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global event storage instance
event_storage = EventStorage()
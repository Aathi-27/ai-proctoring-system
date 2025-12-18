from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from src.config import (
    MONGODB_URI,
    MONGODB_DB,
    MONGODB_EVENTS_COLLECTION,
    MONGODB_STATS_COLLECTION,
)


class MongoDBManager:
    """Manages MongoDB connections and operations."""

    def __init__(self):
        """Initialize MongoDB manager."""
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connect()

    def _connect(self) -> None:
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command("ping")
            self.db = self.client[MONGODB_DB]
        except ConnectionFailure:
            print(f"Warning: Could not connect to MongoDB at {MONGODB_URI}")
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        """
        Check if connected to MongoDB.

        Returns:
            True if connected
        """
        return self.client is not None and self.db is not None

    def insert_event(self, exam_id: str, event: Dict[str, Any]) -> Optional[str]:
        """
        Insert audio event into database.

        Args:
            exam_id: Exam ID
            event: Event data

        Returns:
            Inserted document ID or None if not connected
        """
        if not self.is_connected():
            return None

        try:
            collection = self.db[MONGODB_EVENTS_COLLECTION]
            document = {
                "exam_id": exam_id,
                **event,
                "inserted_at": datetime.utcnow(),
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting event: {e}")
            return None

    def insert_statistics(self, exam_id: str, stats: Dict[str, Any]) -> Optional[str]:
        """
        Insert audio statistics into database.

        Args:
            exam_id: Exam ID
            stats: Statistics data

        Returns:
            Inserted document ID or None if not connected
        """
        if not self.is_connected():
            return None

        try:
            collection = self.db[MONGODB_STATS_COLLECTION]
            document = {
                "exam_id": exam_id,
                **stats,
                "inserted_at": datetime.utcnow(),
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting statistics: {e}")
            return None

    def get_events(
        self, exam_id: str, event_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get events for an exam.

        Args:
            exam_id: Exam ID
            event_type: Optional event type filter
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        if not self.is_connected():
            return []

        try:
            collection = self.db[MONGODB_EVENTS_COLLECTION]
            query = {"exam_id": exam_id}
            if event_type:
                query["event_type"] = event_type

            events = list(
                collection.find(query).sort("timestamp", -1).limit(limit)
            )

            # Convert ObjectId to string
            for event in events:
                if "_id" in event:
                    event["_id"] = str(event["_id"])

            return events
        except Exception as e:
            print(f"Error retrieving events: {e}")
            return []

    def get_statistics(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest statistics for an exam.

        Args:
            exam_id: Exam ID

        Returns:
            Statistics document or None
        """
        if not self.is_connected():
            return None

        try:
            collection = self.db[MONGODB_STATS_COLLECTION]
            result = collection.find_one({"exam_id": exam_id}, sort=[("inserted_at", -1)])

            if result and "_id" in result:
                result["_id"] = str(result["_id"])

            return result
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            return None

    def close(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.close()

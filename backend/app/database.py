from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from .config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            await self.client.admin.command('ping')
            self.db = self.client[settings.database_name]
            self.collection = self.db[settings.collection_name]
            
            await self.collection.create_index([("session_id", 1), ("timestamp", -1)])
            await self.collection.create_index("candidate_id")
            await self.collection.create_index("event_type")
            await self.collection.create_index("received_at")
            
            logger.info(f"Connected to MongoDB at {settings.mongodb_url}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def insert_event(self, event_data: dict):
        try:
            result = await self.collection.insert_one(event_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to insert event: {e}")
            raise

    async def get_events_by_session(self, session_id: str, limit: int = 100):
        try:
            cursor = self.collection.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
            events = await cursor.to_list(length=limit)
            return events
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            raise

    async def get_events_by_candidate(self, candidate_id: str, limit: int = 100):
        try:
            cursor = self.collection.find({"candidate_id": candidate_id}).sort("timestamp", -1).limit(limit)
            events = await cursor.to_list(length=limit)
            return events
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            raise


db = Database()

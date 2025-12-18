from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.database = mongodb.client[settings.database_name]
    await create_indexes()


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()


async def create_indexes():
    await mongodb.database.risk_score_history.create_index([("exam_id", 1), ("session_id", 1), ("timestamp", -1)])
    await mongodb.database.detection_events.create_index([("exam_id", 1), ("session_id", 1), ("timestamp", -1)])


def get_database() -> AsyncIOMotorDatabase:
    return mongodb.database

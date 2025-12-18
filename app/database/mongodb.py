from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class MongoDBClient:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.database = cls.client[settings.database_name]

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        return cls.database

    @classmethod
    def get_events_collection(cls):
        return cls.database[settings.events_collection]


async def get_database():
    return MongoDBClient.get_database()

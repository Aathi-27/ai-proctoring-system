import asyncio
import logging
from app.database import engine, Base, mongo_db
from app import models  # Import models to register them with Base

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

async def init_postgres():
    logger.info("Creating PostgreSQL tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL tables created.")

async def init_mongo():
    logger.info("Initializing MongoDB collections...")
    # Create collections if they don't exist (MongoDB creates them implicitly on insert, but we can explicitly create them with validation or indices here)
    collections = await mongo_db.list_collection_names()
    
    if "events" not in collections:
        await mongo_db.create_collection("events")
        logger.info("Created 'events' collection.")
    
    if "risk_score_history" not in collections:
        await mongo_db.create_collection("risk_score_history")
        logger.info("Created 'risk_score_history' collection.")
        
    # Example: Create indices
    await mongo_db.events.create_index("session_id")
    await mongo_db.risk_score_history.create_index("session_id")
    logger.info("MongoDB initialization complete.")

async def main():
    await init_postgres()
    await init_mongo()

if __name__ == "__main__":
    asyncio.run(main())

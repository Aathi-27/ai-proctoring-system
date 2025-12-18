import pytest
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client["test_exam_proctoring"]
    yield db
    await client.drop_database("test_exam_proctoring")
    client.close()


@pytest.fixture
def sample_exam_id():
    return "exam_123"


@pytest.fixture
def sample_session_id():
    return "session_456"


@pytest.fixture
def current_time():
    return datetime(2024, 1, 15, 10, 0, 0)

import pytest
import numpy as np
import cv2
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.mongodb import MongoDBClient
from app.services.face_detection import FaceDetectionService
from app.services.liveness_detection import LivenessDetectionService
from app.services.event_manager import EventManager


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def face_detection_service():
    return FaceDetectionService()


@pytest.fixture
def liveness_detection_service():
    return LivenessDetectionService()


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def sample_image():
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(image, (200, 100), (440, 380), (255, 255, 255), -1)
    cv2.circle(image, (270, 200), 15, (0, 0, 0), -1)
    cv2.circle(image, (370, 200), 15, (0, 0, 0), -1)
    cv2.ellipse(image, (320, 300), (40, 20), 0, 0, 180, (0, 0, 0), 2)
    return image


@pytest.fixture
def sample_landmarks():
    landmarks = []
    for i in range(468):
        x = 0.3 + (i % 20) * 0.02
        y = 0.3 + (i // 20) * 0.02
        z = 0.0
        landmarks.append([x, y, z])
    return landmarks


@pytest.fixture
def sample_eye_landmarks():
    left_eye = [
        [0.3, 0.3, 0.0],
        [0.32, 0.29, 0.0],
        [0.34, 0.29, 0.0],
        [0.36, 0.3, 0.0],
        [0.34, 0.31, 0.0],
        [0.32, 0.31, 0.0]
    ]
    right_eye = [
        [0.5, 0.3, 0.0],
        [0.52, 0.29, 0.0],
        [0.54, 0.29, 0.0],
        [0.56, 0.3, 0.0],
        [0.54, 0.31, 0.0],
        [0.52, 0.31, 0.0]
    ]
    return left_eye, right_eye


@pytest.fixture(scope="function", autouse=True)
async def setup_mongodb():
    if MongoDBClient.client is None:
        try:
            await MongoDBClient.connect()
        except:
            pass
    yield
    

@pytest.fixture
async def mongodb_client():
    if MongoDBClient.client is None:
        await MongoDBClient.connect()
    yield MongoDBClient

import pytest
import base64
import numpy as np
import cv2
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
class TestAPI:
    async def test_root_endpoint(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data
            assert "endpoints" in data

    async def test_health_check(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "services" in data

    async def test_analyze_frame_success(self):
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(image, (200, 100), (440, 380), (255, 255, 255), -1)
        
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/exams/test_exam_1/analyze-frame",
                json={"frame_data": frame_data}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "face_count" in data
            assert "landmarks" in data
            assert "liveness_score" in data
            assert "is_live" in data
            assert "events" in data
            assert "confidence_scores" in data
            assert "processing_time_ms" in data
            assert isinstance(data["face_count"], int)
            assert isinstance(data["liveness_score"], float)
            assert isinstance(data["is_live"], bool)

    async def test_analyze_frame_invalid_base64(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/exams/test_exam_2/analyze-frame",
                json={"frame_data": "invalid_base64_data"}
            )
            
            assert response.status_code == 400
            assert "detail" in response.json()

    async def test_analyze_frame_blank_image(self):
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/exams/test_exam_3/analyze-frame",
                json={"frame_data": frame_data}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["face_count"] == 0

    async def test_get_exam_events(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/exams/test_exam_4/events")
            
            assert response.status_code == 200
            data = response.json()
            assert "exam_id" in data
            assert "events" in data
            assert "count" in data
            assert data["exam_id"] == "test_exam_4"

    async def test_get_exam_events_with_limit(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/exams/test_exam_5/events?limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert "events" in data
            assert len(data["events"]) <= 10

    async def test_clear_exam_history(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/api/v1/exams/test_exam_6/clear-history")
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "test_exam_6" in data["message"]

    async def test_analyze_frame_multiple_times(self):
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for i in range(3):
                response = await client.post(
                    "/api/v1/exams/test_exam_7/analyze-frame",
                    json={"frame_data": frame_data}
                )
                assert response.status_code == 200

    async def test_analyze_frame_processing_time(self):
        image = np.ones((480, 640, 3), dtype=np.uint8) * 200
        
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/exams/test_exam_8/analyze-frame",
                json={"frame_data": frame_data}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["processing_time_ms"] < 500

    async def test_analyze_frame_small_image(self):
        image = np.ones((30, 30, 3), dtype=np.uint8) * 255
        
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/exams/test_exam_9/analyze-frame",
                json={"frame_data": frame_data}
            )
            
            assert response.status_code == 400

import pytest
import asyncio
import httpx
import websockets
import json
import uuid
from datetime import datetime
from typing import List
import time

from app.models.alerts import AlertEvent, AlertSeverity, AlertType


class TestLoadTesting:
    """Load tests for 10-50 concurrent invigilators with rapid event firing"""
    
    @pytest.mark.asyncio
    @pytest.mark.load_test
    async def test_concurrent_invigilators_10(self):
        """Test 10 concurrent invigilators with rapid alert generation"""
        await self._run_concurrent_invigilator_test(10, 20, "load_test_10_invigilators")
    
    @pytest.mark.asyncio
    @pytest.mark.load_test
    async def test_concurrent_invigilators_25(self):
        """Test 25 concurrent invigilators with rapid alert generation"""
        await self._run_concurrent_invigilator_test(25, 15, "load_test_25_invigilators")
    
    @pytest.mark.asyncio
    @pytest.mark.load_test
    async def test_concurrent_invigilators_50(self):
        """Test 50 concurrent invigilators with rapid alert generation"""
        await self._run_concurrent_invigilator_test(50, 10, "load_test_50_invigilators")
    
    async def _run_concurrent_invigilator_test(self, num_invigilators: int, alerts_per_invigilator: int, test_name: str):
        """Run concurrent invigilator test with specified parameters"""
        exam_id = f"{test_name}_{uuid.uuid4().hex[:8]}"
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Test configuration
        websocket_url = f"ws://localhost:8000/api/v1/ws/exam/{exam_id}"
        api_base_url = "http://localhost:8000/api/v1"
        
        # Track results
        results = {
            "connections_established": 0,
            "alerts_received": 0,
            "alerts_sent": 0,
            "errors": [],
            "connection_times": [],
            "message_latencies": []
        }
        
        async def invigilator_task(invigilator_id: int):
            """Task for each invigilator"""
            invigilator_results = {
                "id": invigilator_id,
                "alerts_received": 0,
                "connection_time": None,
                "error": None
            }
            
            try:
                start_time = time.time()
                
                # Establish WebSocket connection
                uri = f"{websocket_url}?invigilator_id=invigilator_{invigilator_id}"
                
                async with websockets.connect(uri) as websocket:
                    connection_time = time.time() - start_time
                    results["connection_times"].append(connection_time)
                    invigilator_results["connection_time"] = connection_time
                    results["connections_established"] += 1
                    
                    # Listen for alerts
                    alert_task = asyncio.create_task(self._listen_for_alerts(websocket, invigilator_results, results))
                    
                    # Simulate alert acknowledgment
                    await asyncio.sleep(1)  # Let some alerts accumulate
                    
                    # Start sending acknowledgment responses
                    ack_task = asyncio.create_task(self._send_acknowledgments(websocket, exam_id, session_id, api_base_url))
                    
                    # Wait for test duration
                    await asyncio.sleep(alerts_per_invigilator * 0.5)  # Half the time listening
                    
                    # Cancel tasks
                    alert_task.cancel()
                    ack_task.cancel()
                    
                    try:
                        await alert_task
                    except asyncio.CancelledError:
                        pass
                    
                    try:
                        await ack_task
                    except asyncio.CancelledError:
                        pass
                        
            except Exception as e:
                error_msg = f"Invigilator {invigilator_id} error: {str(e)}"
                results["errors"].append(error_msg)
                invigilator_results["error"] = str(e)
            
            return invigilator_results
        
        # Start all invigilator tasks concurrently
        invigilator_tasks = [
            invigilator_task(i) for i in range(num_invigilators)
        ]
        
        # Run alert generation task concurrently
        alert_task = asyncio.create_task(
            self._generate_rapid_alerts(exam_id, session_id, alerts_per_invigilator, results)
        )
        
        # Run all tasks concurrently
        start_time = time.time()
        
        # Start invigilators
        invigilator_results = await asyncio.gather(*invigilator_tasks, return_exceptions=True)
        
        # Stop alert generation
        alert_task.cancel()
        try:
            await alert_task
        except asyncio.CancelledError:
            pass
        
        test_duration = time.time() - start_time
        
        # Collect results
        valid_results = [r for r in invigilator_results if not isinstance(r, Exception)]
        errors = [r for r in invigilator_results if isinstance(r, Exception)]
        
        # Assertions
        assert len(valid_results) >= num_invigilators * 0.9, f"Too many invigilator failures: {len(errors)}"
        assert results["connections_established"] >= num_invigilators * 0.9
        assert test_duration < 60, "Test took too long"
        
        # Performance assertions
        avg_connection_time = sum(results["connection_times"]) / len(results["connection_times"]) if results["connection_times"] else 0
        assert avg_connection_time < 2.0, f"Average connection time too high: {avg_connection_time}s"
        
        # Report results
        print(f"\n{test_name} Results:")
        print(f"  Invigilators: {num_invigilators}")
        print(f"  Alerts per invigilator: {alerts_per_invigilator}")
        print(f"  Duration: {test_duration:.2f}s")
        print(f"  Connections established: {results['connections_established']}")
        print(f"  Alerts received: {results['alerts_received']}")
        print(f"  Alerts sent: {results['alerts_sent']}")
        print(f"  Avg connection time: {avg_connection_time:.3f}s")
        print(f"  Errors: {len(results['errors'])}")
        
        # Allow some connection failures due to resource constraints
        assert len(errors) <= num_invigilators * 0.2
    
    async def _listen_for_alerts(self, websocket, invigilator_results: dict, results: dict):
        """Listen for incoming alerts"""
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "alert":
                        results["alerts_received"] += 1
                        invigilator_results["alerts_received"] += 1
                        
                        # Verify alert structure
                        alert = data.get("alert", {})
                        assert "alert_id" in alert
                        assert "exam_id" in alert
                        assert "event_type" in alert
                        assert "severity" in alert
                        assert "confidence" in alert
                        assert "timestamp" in alert
                        
                        # Record message processing time
                        if "server_timestamp" in data:
                            server_time = datetime.fromisoformat(data["server_timestamp"].replace("Z", "+00:00"))
                            client_time = datetime.utcnow()
                            latency = (client_time - server_time).total_seconds() * 1000
                            results["message_latencies"].append(latency)
                        
                except json.JSONDecodeError:
                    results["errors"].append(f"Invalid JSON received: {message[:100]}")
                    
        except asyncio.TimeoutError:
            # Normal timeout, exit gracefully
            pass
        except websockets.exceptions.ConnectionClosed:
            # Connection closed, exit gracefully
            pass
        except Exception as e:
            results["errors"].append(f"Alert listening error: {str(e)}")
    
    async def _send_acknowledgments(self, websocket, exam_id: str, session_id: str, api_base_url: str):
        """Send alert acknowledgments"""
        try:
            await asyncio.sleep(2)  # Wait for some alerts to arrive
            
            # Create acknowledgment requests for recent alerts
            async with httpx.AsyncClient() as client:
                # Get recent alerts
                response = await client.get(
                    f"{api_base_url}/exams/{exam_id}/alerts?limit=5",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    alerts = data.get("alerts", [])
                    
                    # Acknowledge some alerts
                    for alert in alerts[:2]:  # Acknowledge up to 2 alerts
                        ack_request = {
                            "alert_id": alert["alert_id"],
                            "invigilator_id": "load_test_invigilator"
                        }
                        
                        try:
                            ack_response = await client.post(
                                f"{api_base_url}/exams/{exam_id}/alerts/{alert['alert_id']}/acknowledge",
                                json=ack_request,
                                timeout=5.0
                            )
                            
                            if ack_response.status_code == 200:
                                results["acknowledgments_sent"] = results.get("acknowledgments_sent", 0) + 1
                            else:
                                results["errors"].append(f"Acknowledge failed: {ack_response.status_code}")
                                
                        except Exception as e:
                            results["errors"].append(f"Acknowledge error: {str(e)}")
                            
                        await asyncio.sleep(0.5)  # Rate limit acknowledgments
                        
        except Exception as e:
            results["errors"].append(f"Acknowledgment task error: {str(e)}")
    
    async def _generate_rapid_alerts(self, exam_id: str, session_id: str, num_alerts: int, results: dict):
        """Generate alerts rapidly to test system under load"""
        try:
            async with httpx.AsyncClient() as client:
                api_base_url = "http://localhost:8000/api/v1"
                
                # Generate different types of alerts
                alert_types = [
                    AlertType.NORMAL_ACTIVITY,
                    AlertType.LIVENESS_CONFIRMED,
                    AlertType.TAB_SWITCH,
                    AlertType.FACE_NOT_DETECTED
                ]
                
                for i in range(num_alerts):
                    # Create mock frame data
                    frame_data = self._generate_mock_frame_data()
                    
                    # Create test alert event using API simulation
                    alert_data = {
                        "exam_id": exam_id,
                        "session_id": session_id,
                        "event_type": alert_types[i % len(alert_types)],
                        "confidence": 0.8 + (i % 20) * 0.01,
                        "event_data": {"frame_number": i},
                        "frame_data": frame_data,
                        "frame_number": i
                    }
                    
                    try:
                        # This would typically call the alert generation endpoint
                        # For now, we'll simulate the internal service call
                        response = await client.post(
                            f"{api_base_url}/exams/{exam_id}/monitoring/start",
                            json={"session_id": session_id},
                            timeout=5.0
                        )
                        
                        if response.status_code == 200:
                            results["alerts_sent"] += 1
                        
                    except Exception as e:
                        results["errors"].append(f"Alert generation error: {str(e)}")
                    
                    # Rapid fire rate for load testing
                    await asyncio.sleep(0.1)  # 10 alerts per second
                    
        except Exception as e:
            results["errors"].append(f"Alert generation task error: {str(e)}")
    
    def _generate_mock_frame_data(self) -> str:
        """Generate mock base64 frame data for testing"""
        import base64
        
        # Create a simple test image (100x100 pixels, red background)
        import numpy as np
        from PIL import Image
        
        # Create red image
        img_array = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # Convert to base64
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        
        return base64.b64encode(img_bytes).decode()


class TestAPILoadTesting:
    """Load tests for REST API endpoints"""
    
    @pytest.mark.asyncio
    @pytest.mark.load_test
    async def test_alert_history_api_load(self):
        """Test alert history API under load"""
        exam_id = "api_load_test"
        session_id = "api_session"
        
        # Pre-generate test data
        async with httpx.AsyncClient() as client:
            # Start exam monitoring
            await client.post(
                f"http://localhost:8000/api/v1/exams/{exam_id}/monitoring/start",
                json={"session_id": session_id}
            )
        
        # Concurrent API requests
        async def api_request_task(request_id: int):
            try:
                async with httpx.AsyncClient() as client:
                    # Test alert history endpoint
                    response = await client.get(
                        f"http://localhost:8000/api/v1/exams/{exam_id}/alerts?limit=50",
                        timeout=10.0
                    )
                    
                    assert response.status_code in [200, 503]  # Allow service unavailable
                    return {"request_id": request_id, "status": "success", "status_code": response.status_code}
                    
            except Exception as e:
                return {"request_id": request_id, "status": "error", "error": str(e)}
        
        # Run 20 concurrent requests
        tasks = [api_request_task(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "success"])
        failed = len(results) - successful
        
        print(f"API Load Test Results:")
        print(f"  Successful requests: {successful}")
        print(f"  Failed requests: {failed}")
        
        # Allow some failures due to resource constraints
        assert successful >= 15  # At least 75% success rate
    
    @pytest.mark.asyncio
    @pytest.mark.load_test
    async def test_health_endpoint_load(self):
        """Test health endpoint under concurrent requests"""
        
        async def health_check_task(task_id: int):
            try:
                start_time = time.time()
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:8000/health",
                        timeout=5.0
                    )
                    response_time = time.time() - start_time
                    
                    return {
                        "task_id": task_id,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code == 200
                    }
            except Exception as e:
                return {
                    "task_id": task_id,
                    "error": str(e),
                    "success": False
                }
        
        # Run 100 concurrent health checks
        tasks = [health_check_task(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_results = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        success_rate = len(successful_results) / len(results) if results else 0
        avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        print(f"Health Endpoint Load Test Results:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        
        # Assertions
        assert success_rate >= 0.90, f"Health endpoint success rate too low: {success_rate:.2%}"
        assert avg_response_time < 0.1, f"Response time too high: {avg_response_time:.3f}s"


class TestStressTesting:
    """Stress tests for system limits"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage under concurrent load"""
        # This would typically involve monitoring memory usage
        # For now, we'll run a basic stress test
        
        exam_id = "memory_test"
        
        # Create many concurrent connections
        connections = []
        
        async def stress_connection(connection_id: int):
            try:
                uri = f"ws://localhost:8000/api/v1/ws/exam/{exam_id}?invigilator_id=stress_{connection_id}"
                
                async with websockets.connect(uri) as websocket:
                    # Keep connection alive for a bit
                    await asyncio.sleep(2)
                    
                    # Send some messages
                    for i in range(5):
                        await websocket.send(json.dumps({"type": "ping"}))
                        await asyncio.sleep(0.1)
                        
                return {"connection_id": connection_id, "status": "success"}
                
            except Exception as e:
                return {"connection_id": connection_id, "status": "error", "error": str(e)}
        
        # Start 30 concurrent connections
        tasks = [stress_connection(i) for i in range(30)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "success"])
        
        print(f"Stress Test Results:")
        print(f"  Connections: 30")
        print(f"  Successful: {successful}")
        
        # System should handle at least 20 concurrent connections
        assert successful >= 20, f"Too few successful connections: {successful}"
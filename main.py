"""
Main entry point for YOLOv8 Mobile Detection System.

Command-line interface for starting the API server, running tests, and administration.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import detection_config, api_config
from src.database.event_storage import event_storage


async def run_health_check():
    """Run system health check."""
    try:
        from src.api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ System health check passed")
            data = response.json()
            print(f"Status: {data.get('message', 'Unknown')}")
            return True
        else:
            print("❌ System health check failed")
            print(f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def run_server():
    """Start the FastAPI server."""
    import uvicorn
    
    print("🚀 Starting YOLOv8 Mobile Detection API")
    print("=" * 50)
    print(f"Host: {api_config.host}:{api_config.port}")
    print(f"Model: {detection_config.model_name}")
    print(f"Debug: {api_config.debug}")
    print("=" * 50)
    
    # Start server
    uvicorn.run(
        "src.api.main:app",
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug,
        log_level="info" if not api_config.debug else "debug"
    )


async def run_tests():
    """Run the test suite."""
    import pytest
    
    print("🧪 Running YOLOv8 Detection System Tests")
    print("=" * 50)
    
    # Run pytest
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short"
    ])
    
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return exit_code


def download_models():
    """Download YOLOv8 models."""
    try:
        from ultralytics import YOLO
        
        print("📥 Downloading YOLOv8 models...")
        
        # Download nano model
        print("Downloading yolov8n.pt...")
        yolo_nano = YOLO("yolov8n.pt")
        print("✅ yolov8n.pt downloaded")
        
        # Download small model
        print("Downloading yolov8s.pt...")
        yolo_small = YOLO("yolov8s.pt")
        print("✅ yolov8s.pt downloaded")
        
        print("✅ Models downloaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to download models: {e}")
        return False
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YOLOv8 Mobile Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["server", "test", "health", "download-models"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="API server port"
    )
    
    args = parser.parse_args()
    
    # Override settings
    if args.debug:
        api_config.debug = True
        detection_config.max_processing_time_ms = 1000
    
    if args.port:
        api_config.port = args.port
    
    # Execute command
    try:
        if args.command == "server":
            run_server()
        
        elif args.command == "test":
            exit_code = asyncio.run(run_tests())
            sys.exit(exit_code)
        
        elif args.command == "health":
            success = asyncio.run(run_health_check())
            sys.exit(0 if success else 1)
        
        elif args.command == "download-models":
            success = download_models()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
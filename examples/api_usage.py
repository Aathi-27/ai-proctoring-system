#!/usr/bin/env python3
"""
Example of using the Audio VAD Pipeline API.
"""

import requests
import numpy as np
import io
from scipy.io.wavfile import write
import json


API_BASE_URL = "http://localhost:5000"


def create_sample_audio(duration_s: float = 1.0) -> bytes:
    """
    Create sample WAV audio.
    
    Args:
        duration_s: Duration in seconds
        
    Returns:
        WAV file as bytes
    """
    sample_rate = 16000
    samples = int(sample_rate * duration_s)
    t = np.arange(samples) / sample_rate
    
    # Create 500 Hz sine wave
    audio = np.sin(2 * np.pi * 500 * t) * 0.5
    audio = (audio * 32767).astype(np.int16)
    
    # Write to WAV format
    wav_buffer = io.BytesIO()
    write(wav_buffer, sample_rate, audio)
    wav_buffer.seek(0)
    
    return wav_buffer.getvalue()


def health_check():
    """Check API health."""
    print("1. Health Check")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")


def analyze_audio(exam_id: str):
    """Analyze audio."""
    print(f"\n2. Analyze Audio (Exam: {exam_id})")
    
    # Create sample audio
    audio_data = create_sample_audio(duration_s=2.0)
    
    # Send request
    response = requests.post(
        f"{API_BASE_URL}/exams/{exam_id}/analyze-audio",
        data=audio_data,
        headers={"Content-Type": "audio/wav"}
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    print(f"   VAD Score: {data.get('vad_score', 'N/A')}")
    print(f"   Background Speech: {data.get('background_speech_detected', 'N/A')}")
    print(f"   Speaker Count: {data.get('speaker_count', 'N/A')}")
    print(f"   Events: {len(data.get('events', []))}")


def analyze_buffer(exam_id: str):
    """Analyze buffer."""
    print(f"\n3. Analyze Buffer (Exam: {exam_id})")
    
    response = requests.get(
        f"{API_BASE_URL}/exams/{exam_id}/analyze-buffer"
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    print(f"   Buffer Duration: {data.get('buffer_duration_s', 'N/A')}s")
    print(f"   Speech %: {data.get('speech_percentage', 'N/A')}")
    print(f"   Silence %: {data.get('silence_percentage', 'N/A')}")


def get_statistics(exam_id: str):
    """Get statistics."""
    print(f"\n4. Get Statistics (Exam: {exam_id})")
    
    response = requests.get(
        f"{API_BASE_URL}/exams/{exam_id}/statistics"
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    stats = data.get('statistics', {})
    
    print(f"   Total Frames: {stats.get('total_frames', 'N/A')}")
    print(f"   VAD Frames: {stats.get('vad_frames', 'N/A')}")
    print(f"   Speech %: {stats.get('speech_percentage', 'N/A')}")
    print(f"   Avg VAD Score: {stats.get('avg_vad_score', 'N/A')}")


def get_events(exam_id: str, event_type: str = None):
    """Get events."""
    print(f"\n5. Get Events (Exam: {exam_id})")
    
    params = {}
    if event_type:
        params['event_type'] = event_type
    
    response = requests.get(
        f"{API_BASE_URL}/exams/{exam_id}/events",
        params=params
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    print(f"   Event Count: {data.get('count', 0)}")
    
    events = data.get('events', [])
    if events:
        print("   Recent Events:")
        for event in events[:3]:
            print(f"     - {event.get('event_type', 'Unknown')}: "
                  f"{json.dumps(event.get('data', {}))}")


def reset_analysis(exam_id: str):
    """Reset analysis."""
    print(f"\n6. Reset Analysis (Exam: {exam_id})")
    
    response = requests.post(
        f"{API_BASE_URL}/exams/{exam_id}/reset"
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")


def shutdown_analysis(exam_id: str):
    """Shutdown analysis."""
    print(f"\n7. Shutdown Analysis (Exam: {exam_id})")
    
    response = requests.post(
        f"{API_BASE_URL}/exams/{exam_id}/shutdown"
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")


def main():
    """Main demonstration."""
    
    print("=" * 60)
    print("Audio VAD Pipeline - API Usage Example")
    print("=" * 60)
    print("\nNote: Ensure the server is running with:")
    print("  python main.py --host 0.0.0.0 --port 5000\n")
    
    try:
        exam_id = "api_demo_001"
        
        # Run examples
        health_check()
        analyze_audio(exam_id)
        analyze_buffer(exam_id)
        get_statistics(exam_id)
        get_events(exam_id)
        get_events(exam_id, event_type="VAD_DETECTED")
        reset_analysis(exam_id)
        
        # Process more audio
        print("\n8. Processing more audio...")
        analyze_audio(exam_id)
        get_statistics(exam_id)
        
        # Shutdown
        shutdown_analysis(exam_id)
        
        print("\n" + "=" * 60)
        print("API demo completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Please ensure the server is running.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

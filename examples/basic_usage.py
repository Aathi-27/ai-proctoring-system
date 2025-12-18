#!/usr/bin/env python3
"""
Basic usage example for the Audio VAD Pipeline.
"""

import numpy as np
import sys
sys.path.insert(0, '..')

from src.audio_pipeline import AudioAnalysisPipeline
from src.config import SAMPLE_RATE, FRAME_SIZE


def create_synthetic_audio(duration_s: float, frequency: float = 500) -> np.ndarray:
    """
    Create synthetic audio for demonstration.
    
    Args:
        duration_s: Duration in seconds
        frequency: Frequency in Hz
        
    Returns:
        Audio data (16 kHz, mono)
    """
    samples = int(SAMPLE_RATE * duration_s)
    t = np.arange(samples) / SAMPLE_RATE
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32) * 0.5
    return audio


def main():
    """Main demonstration."""
    
    print("=" * 60)
    print("Audio VAD Pipeline - Basic Usage Example")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = AudioAnalysisPipeline(exam_id="demo_exam_001")
    
    # Create synthetic audio
    print("2. Creating synthetic audio...")
    duration = 3.0
    audio = create_synthetic_audio(duration, frequency=500)
    
    # Process in chunks
    print(f"3. Processing {duration}s of audio in {FRAME_SIZE}-sample chunks...")
    chunk_count = 0
    vad_scores = []
    
    for i in range(0, len(audio), FRAME_SIZE):
        chunk = audio[i:i+FRAME_SIZE]
        if len(chunk) < FRAME_SIZE:
            # Pad last chunk
            chunk = np.pad(chunk, (0, FRAME_SIZE - len(chunk)))
        
        result = pipeline.process_audio_chunk(chunk)
        vad_scores.append(result["vad_score"])
        chunk_count += 1
        
        if chunk_count % 10 == 0:
            print(f"   Processed {chunk_count} chunks | VAD: {result['vad_score']:.3f} | "
                  f"Background: {result['background_speech_detected']} | "
                  f"Multiple: {result['multiple_voices_detected']}")
    
    # Analyze buffer
    print("\n4. Analyzing buffer...")
    buffer_analysis = pipeline.analyze_buffer()
    
    print(f"   Buffer duration: {buffer_analysis['buffer_duration_s']:.2f}s")
    print(f"   Speech: {buffer_analysis['speech_percentage']:.1f}%")
    print(f"   Silence: {buffer_analysis['silence_percentage']:.1f}%")
    print(f"   Timestamp count: {len(buffer_analysis['speech_timestamps'])}")
    
    # Get statistics
    print("\n5. Statistics...")
    stats = pipeline._calculate_statistics()
    
    print(f"   Total frames: {stats['total_frames']}")
    print(f"   VAD frames: {stats['vad_frames']}")
    print(f"   Speech %: {stats['speech_percentage']:.1f}%")
    print(f"   Avg VAD score: {stats['avg_vad_score']:.3f}")
    print(f"   Max VAD score: {stats['max_vad_score']:.3f}")
    print(f"   Min VAD score: {stats['min_vad_score']:.3f}")
    print(f"   Background speech events: {stats['background_speech_events']}")
    print(f"   Multiple voices events: {stats['multiple_voices_events']}")
    
    # Get events
    print("\n6. Events generated:")
    events = pipeline.event_manager.get_events()
    print(f"   Total events: {len(events)}")
    
    if events:
        event_types = {}
        for event in events:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("   Event breakdown:")
        for event_type, count in event_types.items():
            print(f"     - {event_type}: {count}")
    
    # Log to database (if configured)
    print("\n7. Logging to database...")
    db_result = pipeline.log_events_to_db()
    print(f"   Events logged: {db_result}")
    
    stats_result = pipeline.log_statistics_to_db()
    print(f"   Statistics logged: {stats_result}")
    
    # Cleanup
    print("\n8. Cleanup...")
    pipeline.shutdown()
    print("   Pipeline shutdown complete")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
